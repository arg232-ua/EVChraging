import sys
import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import threading
import socket

TOPIC_REGISTROS = "registros_cp"
TOPIC_COMANDOS  = "comandos_cp"
TOPIC_ESTADO    = "estado_cp"
TOPIC_CARGA_SOLICITADA = "CARGA_SOLICITADA"

ESTADOS_VALIDOS = {"ACTIVADO", "PARADO", "AVERIA", "SUMINISTRANDO", "DESCONECTADO"}

def obtener_productor(servidor_kafka):
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        linger_ms=10,
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka, auto_offset_reset="latest"):
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id=grupo_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )

class EV_CP:
    def __init__(self, servidor_kafka, cp_id, ubicacion="N/A", precio_eur_kwh=0.35):
        self.servidor_kafka = servidor_kafka
        self.cp_id = cp_id
        self.ubicacion = ubicacion
        self.precio = float(precio_eur_kwh)
        self.estado = "ACTIVADO"
        self.enchufado = False

        self.productor = None

        self.cargando = False
        self.driver_en_carga = None
        self.potencia_kw = 7.4
        self.energia_kwh = 0.0
        self.importe_eur = 0.0

        self._lock_carga = threading.Lock()
        self._stop_carga = threading.Event()
        self._hilo_carga = None

        self.puerto_socket = None
        self._sock_srv = None
        self._sock_thread = None
        self._stop_sock = threading.Event()
        self.fallo_local = False

    def conectar(self):
        self.productor = obtener_productor(self.servidor_kafka)
        for _ in range(10):
            if self.productor.bootstrap_connected():
                print(f"[EV_CP_E] Conectado a Kafka en {self.servidor_kafka}")
                return True
            time.sleep(0.2)
        print(f"[EV_CP_E] No fue posible conectar con Kafka en {self.servidor_kafka}")
        return False

    def registrar_cp(self): #
        datos = {
            "tipo": "REGISTRO_CP",
            "ts": datetime.utcnow().isoformat(),
            "cp_id": self.cp_id,
            "ubicacion": self.ubicacion,
            "precio_eur_kwh": self.precio,
            "estado_inicial": self.estado
        }
        self.productor.send(TOPIC_REGISTROS, key=self.cp_id, value=datos)
        self.productor.flush()
        print(f"[EV_CP_E] Registrado CP '{self.cp_id}' en tópico '{TOPIC_REGISTROS}'.")

    def enviar_estado(self, nuevo_estado: str, motivo: str = "", fin=False):
        if nuevo_estado not in ESTADOS_VALIDOS:
            print(f"[EV_CP_E] Estado ignorado (no válido): {nuevo_estado}")
            return

        self.estado = nuevo_estado
        datos = {
            "ts": datetime.utcnow().isoformat(),
            "cp_id": self.cp_id,
            "estado": self.estado,
            "motivo": motivo,
            "precio_eur_kwh": self.precio
        }
        if self.cargando or nuevo_estado == "SUMINISTRANDO":
            datos.update({
                "driver_id": self.driver_en_carga,
                "energia_kwh": round(self.energia_kwh, 6),
                "importe_eur": round(self.importe_eur, 4),
                "potencia_kw": self.potencia_kw
            })
        if fin:
            datos["fin_carga"] = True

        self.productor.send(TOPIC_ESTADO, key=self.cp_id, value=datos)
        self.productor.flush()
        print(f"[EV_CP_E] Estado publicado -> {self.cp_id}: {self.estado} ({motivo})")

    def _handle_command(self, msg: dict):
        cmd = (msg.get("cmd") or "").upper()
        meta = msg.get("meta") or {}

        if cmd == "PARAR":
            if self.cargando:
                self.finalizar_carga(motivo="Parada por CENTRAL")
            self.enviar_estado("PARADO", motivo="Central ordena PARAR")

        elif cmd == "REANUDAR":
            self.enviar_estado("ACTIVADO", motivo="Central ordena REANUDAR")

        elif cmd == "AVERIA":
            if self.cargando:
                self.finalizar_carga(motivo="Avería detectada; sesión abortada")
            self.enviar_estado("AVERIA", motivo="Central marca AVERIA")

        elif cmd == "ACTIVADO":
            self.enviar_estado("ACTIVADO", motivo="Central marca RECUPERADO")

        elif cmd == "INICIAR_CARGA":
            driver_id = meta.get("driver_id")
            potencia_kw = meta.get("potencia_kw")
            if not driver_id:
                print("[EV_CP_E] INICIAR_CARGA sin driver_id -> ignorado.")
                return
            if self.estado in ("PARADO", "AVERIA", "DESCONECTADO"):
                print(f"[EV_CP_E] INICIAR_CARGA bloqueado en estado {self.estado}.")
                return
            while not self.enchufado:
                time.sleep(0.5)

        elif cmd == "FINALIZAR_CARGA":
            self.finalizar_carga(motivo="Orden de CENTRAL")

        else:
            print(f"[EV_CP_E] Comando no reconocido (ignorado): {cmd}")

    def escuchar_comandos(self):
        try:
            consumidor = obtener_consumidor(
                topico=TOPIC_COMANDOS,
                grupo_id=f"cp_{self.cp_id}",
                servidor_kafka=self.servidor_kafka,
                auto_offset_reset="latest"
            )
            print(f"[EV_CP_E] Escuchando comandos en '{TOPIC_COMANDOS}' (grupo=cp_{self.cp_id})...")
            for record in consumidor:
                msg = record.value
                if not isinstance(msg, dict):
                    continue
                destino = msg.get("cp_id")
                if destino not in (self.cp_id, "ALL"):
                    continue
                self._handle_command(msg)
        except Exception as e:
            print(f"[EV_CP_E] Error en escuchar_comandos: {e}")

    def _bucle_carga(self):
        try:
            while not self._stop_carga.is_set():
                time.sleep(1.0)
                with self._lock_carga:
                    self.energia_kwh += (self.potencia_kw / 3600.0)
                    self.importe_eur = self.energia_kwh * self.precio
                self.enviar_estado("SUMINISTRANDO", motivo="Telemetría en curso")
        except Exception as e:
            print(f"[EV_CP_E] Error en _bucle_carga: {e}")

    def iniciar_carga(self, driver_id: str, potencia_kw: float = None):
        with self._lock_carga:
            # Bloquear inicio si el CP está en un estado que impide suministrar
            if self.estado in ("PARADO", "AVERIA", "DESCONECTADO"):
                print(f"[EV_CP_E] Inicio de carga BLOQUEADO: estado actual={self.estado}")
                # Notificamos a CENTRAL que hubo un intento local bloqueado
                try:
                    self.enviar_estado(self.estado, motivo="Intento local de iniciar suministro bloqueado")
                except Exception:
                    pass
                return
            if self.cargando:
                print("[EV_CP_E] Ya hay una carga en curso; ignorando INICIAR_CARGA.")
                return

            # Si no se proporciona driver_id, usamos un identificador sintético del poste
            if not driver_id:
                driver_id = f"POSTE_{self.cp_id}"

            self.cargando = True
            self.driver_en_carga = driver_id
            if potencia_kw:
                self.potencia_kw = float(potencia_kw)
            self.energia_kwh = 0.0
            self.importe_eur = 0.0
            self._stop_carga.clear()
        
        self.enviar_estado("SUMINISTRANDO", motivo="Inicio de carga")
        self._hilo_carga = threading.Thread(target=self._bucle_carga, daemon=True)
        self._hilo_carga.start()

    def finalizar_carga(self, motivo: str = "Fin de carga"):
        with self._lock_carga:
            if not self.cargando:
                print("[EV_CP_E] No hay carga en curso; ignorando FINALIZAR_CARGA.")
                return
            self._stop_carga.set()
        if self._hilo_carga:
            self._hilo_carga.join(timeout=2.0)

        self.enviar_estado("SUMINISTRANDO", motivo=motivo, fin=True)

        with self._lock_carga:
            self.cargando = False
            self.driver_en_carga = None
        self.enviar_estado("ACTIVADO", motivo="Libre tras finalizar carga")

    def iniciar_servidor_socket(self, puerto: int):
        self.puerto_socket = int(puerto)
        self._stop_sock.clear()
        self._sock_thread = threading.Thread(target=self._loop_socket, daemon=True)
        self._sock_thread.start()
        print(f"[EV_CP_E] Socket de monitorización escuchando en 0.0.0.0:{self.puerto_socket}")

    def solicitar_recarga_local(self, driver_id, potencia_kw):
        """Enviar una solicitud de recarga a CENTRAL (simula que el propio poste la pide).

        El formato es compatible con el que envía `EvDriver`:
        { 'driver_id', 'cp_id', 'type': 'SOLICITAR_RECARGA', 'timestamp' }
        """
        if not self.productor:
            print("[EV_CP_E] Productor Kafka no disponible. No se puede solicitar recarga.")
            return False

        msg = {
            'cp_id': self.cp_id,
            'driver_id': driver_id,
            'type': 'SOLICITAR_RECARGA',
            'timestamp': time.time()
        }
        # Incluir driver_id solo si se proporciona (no obligatorio para solicitud desde el poste)
        if driver_id:
            msg['driver_id'] = driver_id
        if potencia_kw is not None:
            try:
                msg['potencia_kw'] = float(potencia_kw)
            except Exception:
                pass

        try:
            self.productor.send(TOPIC_CARGA_SOLICITADA, key=self.cp_id, value=msg) #Solicita recarga local a central
            self.productor.flush()
            print(f"[EV_CP_E] Solicitud de recarga local enviada para driver '{driver_id}' en CP '{self.cp_id}'")
            return True
        except Exception as e:
            print(f"[EV_CP_E] Error al enviar solicitud de recarga local: {e}")
            return False

    def desconectar_cp(self):
        print(f"[EV_CP_E] Iniciando desconexión del CP {self.cp_id}...")
        
        # 1. Finalizar carga si está en curso
        if self.cargando:
            print("[EV_CP_E] Finalizando carga activa antes de desconectar...")
            self.finalizar_carga(motivo="Desconexión del CP")
        
        # 2. Enviar mensaje de desconexión a la central
        datos_desconexion = {
            "tipo": "DESCONEXION_CP",
            "ts": datetime.utcnow().isoformat(),
            "cp_id": self.cp_id,
            "estado": "DESCONECTADO",
            "motivo": "Desconexión voluntaria desde el CP",
            "ubicacion": self.ubicacion
        }
        
        try:
            self.productor.send(TOPIC_ESTADO, key=self.cp_id, value=datos_desconexion)
            self.productor.flush()
            print(f"[EV_CP_E] Mensaje de desconexión enviado a la central para CP {self.cp_id}")
        except Exception as e:
            print(f"[EV_CP_E] Error al enviar mensaje de desconexión: {e}")
        
        # 3. Actualizar estado local
        self.estado = "DESCONECTADO"
        self.enchufado = False
        
        # 4. Cerrar conexiones
        self.detener_servidor_socket()
        
        # 5. Cerrar productor Kafka
        try:
            if self.productor:
                self.productor.flush(timeout=2.0)
                self.productor.close(timeout=2.0)
                print("[EV_CP_E] Productor Kafka cerrado")
        except Exception as e:
            print(f"[EV_CP_E] Error al cerrar productor Kafka: {e}")
        
        print(f"[EV_CP_E] CP {self.cp_id} completamente desconectado")

    def mostrar_menu_local(self):
        try:
            while True:
                print("\n" + "="*50)
                print("          MENÚ CP ")
                print("="*50)
                print("1. Solicitar recarga localmente (pedir a CENTRAL)")
                print("2. Enchufar (iniciar suministro)")
                print("3. Desenchufar (finalizar suministro)")
                print("4. Poner en PARADO (local)")
                print("5. Reanudar (local)")
                print("6. Ver estado actual")
                print("7. Salir")
                print("="*50)

                opcion = input("Seleccione una opción (1-7): ").strip()

                if opcion == '1':
                    # No pedimos driver_id aquí: la solicitud se hace desde el poste al CENTRAL
                    driver_id = input("Conductor: ").strip()
                    potencia_kw = input("Potencia: ").strip()
                    # Enviamos la solicitud sin driver_id explícito (CENTRAL decidirá la asignación)
                    self.solicitar_recarga_local(driver_id, potencia_kw)

                elif opcion == '2':
                    if self.cargando:
                        print("Ya hay una recarga en curso. Use Desenchufar si desea finalizarla.")
                    else:
                        driver_id = input("Driver_id asociado a la recarga (simulado): ").strip()
                        potencia = input("Potencia (kW) [enter=7.4]: ").strip()
                        potencia_val = None
                        if potencia:
                            try:
                                potencia_val = float(potencia)
                            except Exception:
                                potencia_val = None
                        if not driver_id:
                            print("Debe proporcionar un driver_id para iniciar suministro.")
                        else:
                            self.iniciar_carga(driver_id, potencia_val)
                        self.enchufado = True

                elif opcion == '3':
                    if not self.cargando:
                        print("No hay suministro en curso para finalizar.")
                    else:
                        self.finalizar_carga(motivo="Finalizado localmente (desenchufar)")
                        self.enchufado = False

                elif opcion == '4':
                    if self.cargando:
                        print("Hay una carga en curso; se finalizará antes de poner en PARADO.")
                        self.finalizar_carga(motivo="Parado local: finalizando carga")
                    self.enviar_estado("PARADO", motivo="Parado ordenado localmente")

                elif opcion == '5':
                    # Reanudar: volver a ACTIVADO si no hay avería
                    if self.estado == 'AVERIA':
                        print("El CP está en AVERIA y no puede reanudar hasta resolver la avería.")
                    else:
                        self.enviar_estado("ACTIVADO", motivo="Reanudar ordenado localmente")

                elif opcion == '6':
                    print("\n--- ESTADO CP ---")
                    print(f"CP ID: {self.cp_id}")
                    print(f"Estado: {self.estado}")
                    print(f"Cargando: {'Sí' if self.cargando else 'No'}")
                    if self.cargando:
                        print(f"Driver en carga: {self.driver_en_carga}")
                        print(f"Potencia (kW): {self.potencia_kw}")
                        print(f"Energía (kWh): {self.energia_kwh:.4f}")
                        print(f"Importe (€): {self.importe_eur:.4f}")
                    print(f"Fallo local: {'Sí' if self.fallo_local else 'No'}")
                    print("------------------\n")

                elif opcion == '7':
                    print("Saliendo del menú local...")
                    self.desconectar_cp()
                    break

                else:
                    print("Opción no válida. Intente de nuevo.")

        except KeyboardInterrupt:
            print("\nSaliendo del menú por KeyboardInterrupt...")
        except Exception as e:
            print(f"Error en menú local: {e}")

    def _loop_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(('', self.puerto_socket))
            srv.listen(1)
            self._sock_srv = srv

            while not self._stop_sock.is_set():
                try:
                    srv.settimeout(1.0)
                    try:
                        conn, addr = srv.accept()
                    except socket.timeout:
                        continue

                    with conn:
                        conn.settimeout(2.0)
                        buffer = b""
                        while not self._stop_sock.is_set():
                            try:
                                data = conn.recv(1024)
                                if not data:
                                    break
                                buffer += data
                                while b"\n" in buffer:
                                    line, buffer = buffer.split(b"\n", 1)
                                    self._process_socket_command(conn, line.decode(errors="ignore").strip())
                            except socket.timeout:
                                continue
                            except Exception:
                                break
                except Exception:
                    continue

    def _process_socket_command(self, conn: socket.socket, cmd: str):
        c = (cmd or "").strip().upper()

        if c.startswith("PING"):
            # Esperar: "PING CP3" en lugar de solo "PING"
            partes = c.split()
            cp_solicitado = partes[1] if len(partes) > 1 else None
            
            if cp_solicitado and cp_solicitado != self.cp_id:
                # No es para este CP
                conn.sendall(b"KO\n")
                return
                
            if self.estado == "ACTIVADO" or self.estado == "SUMINISTRANDO":
                respuesta = "OK\n"
            else:
                respuesta = "KO\n"
            conn.sendall(respuesta.encode("utf-8"))


    def detener_servidor_socket(self):
        self._stop_sock.set()
        try:
            with socket.create_connection(("127.0.0.1", self.puerto_socket), timeout=0.2):
                pass
        except Exception:
            pass
        if self._sock_thread:
            self._sock_thread.join(timeout=2.0)

def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Uso: python EV_CP_E.py <IP:puerto_broker> <CP_ID> [<UBICACION>] [<PRECIO_EUR_KWH>] [<PUERTO_SOCKET_ENGINE>]")
        sys.exit(1)

    servidor_kafka = sys.argv[1]
    cp_id = sys.argv[2]
    ubicacion = sys.argv[3] if len(sys.argv) >= 4 else "N/A"
    precio = float(sys.argv[4]) if len(sys.argv) >= 5 else 0.35
    puerto_engine = int(sys.argv[5]) if len(sys.argv) >= 6 else 6001

    print(f"[EV_CP_E] Broker: {servidor_kafka} | CP_ID: {cp_id} | Ubicación: {ubicacion} | Precio: {precio:.2f} €/kWh | PortSock: {puerto_engine}")

    cp = EV_CP(servidor_kafka, cp_id, ubicacion, precio)

    try:
        if not cp.conectar():
            sys.exit(2)

        cp.iniciar_servidor_socket(puerto_engine)
        cp.registrar_cp()
        cp.enviar_estado(cp.estado, motivo="Arranque CP")

        hilo_cmd = threading.Thread(target=cp.escuchar_comandos, daemon=True)
        hilo_cmd.start()

        print("[EV_CP_E] Engine listo: registrado, escuchando comandos y con socket de monitor activo. Use el menú local para acciones (Ctrl+C para salir).")
        # Ejecutamos el menú local en el hilo principal (interfaz de consola)
        cp.mostrar_menu_local()

    except KeyboardInterrupt:
        print("\n[EV_CP_E] Saliendo…")
    finally:
        try:
            cp.detener_servidor_socket()
        except Exception:
            pass
        try:
            if cp.productor is not None:
                cp.productor.flush(1.0)
                cp.productor.close(1.0)
        except Exception:
            pass

if __name__ == "__main__":
    main()
