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
TOPIC_MONITOR   = "monitor_cp"

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
        self.estado = "ACTIVADO"   # Estado inicial

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

    def registrar_cp(self):

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

            elif cmd == "RECUPERADO":
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
                self.iniciar_carga(driver_id, potencia_kw)

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
            if self.cargando:
                print("[EV_CP_E] Ya hay una carga en curso; ignorando INICIAR_CARGA.")
                return
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
                            # Leemos por líneas sencillas
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

            if c == "PING":
                sano = (self.estado != "AVERIA") and (not self.fallo_local)
                respuesta = "OK\n" if sano else "KO\n"
                conn.sendall(respuesta.encode("utf-8"))

            elif c == "STATUS":
                conn.sendall((self.estado + "\n").encode("utf-8"))

            elif c == "FAILON":
                self.fallo_local = True
                conn.sendall(b"ACK\n")

            elif c == "FAILOFF":
                self.fallo_local = False
                conn.sendall(b"ACK\n")

            else:
                conn.sendall(b"NACK\n")

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

    cp = EV_CP(servidor_kafka, cp_id, ubicacion)

    try:
        if not cp.conectar():
            sys.exit(2)

        cp.iniciar_servidor_socket(puerto_engine)
        
        cp.registrar_cp()
                
        cp.enviar_estado(cp.estado, motivo="Arranque CP")

       
        hilo_cmd = threading.Thread(target=cp.escuchar_comandos, daemon=True)
        hilo_cmd.start()

        print("[EV_CP_E] Paso 3 OK: CP registrado. (Aún sin escuchar comandos ni publicar estado). Ctrl+C para salir.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[EV_CP_E] Saliendo…")
    finally:
        try:
            if cp is not None:
                cp.detener_servidor_socket()
        except Exception:
            pass

        try:
            if cp is not None and cp.productor is not None:
                cp.productor.flush(1.0)
                cp.productor.close(1.0)
        except Exception:
            pass


if __name__ == "__main__":
    main()
    
