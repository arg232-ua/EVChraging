from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import sys
import time
import mysql.connector
import socket

TOPIC_REGISTROS = "registros_cp"
TOPIC_COMANDOS  = "comandos_cp"
TOPIC_ESTADO    = "estado_cp"
TOPIC_RESP_DRIVER = "respuestas_conductor"
TOPIC_SOLICITUD   = "CARGA_SOLICITADA"
TOPIC_VERIF       = "conductor"

EST_ACTIVO = "ACTIVADO"
EST_PARADO = "PARADO"
EST_AVERIA = "AVERIA"
EST_SUM    = "SUMINISTRANDO"
EST_DESC   = "DESCONECTADO"


def obtener_productor(servidor_kafka): # Crea un nuevo productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8'), # Forma de codificar los mensajes
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka): # Crea un nuevo consumidor de Kafka
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_deserializer=lambda v: json.loads(v.decode('utf-8')), # Forma de decodificar los mensajes
        group_id = grupo_id, # Identificador del grupo de consumidores
        auto_offset_reset='latest', # Comenzar a leer desde el principio del tópico
    )

def conectar_bd(servidor_bd):
    try:
        ip_bd, puerto_bd = servidor_bd.split(":")
        puerto_bd = int(puerto_bd)

        conexion = mysql.connector.connect(
            host = ip_bd,
            port = puerto_bd,
            user = "sd_remoto",
            password = "1234",
            database = "evcharging"
        )

        print(f"Servidor conectado a la Base de Datos en {servidor_bd}")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la Base de Datos: {e}")
        return None

class EV_Central:
    def __init__(self, servidor_kafka, servidor_bd):
        self.servidor_kafka = servidor_kafka
        self.servidor_bd = servidor_bd
        self.productor = obtener_productor(servidor_kafka)
        self.cps = {}
        self.conexion_bd = None
        self.reconectar_bd()

        self.inicio = time.time()
        print(f"Central inicializada y conectada a Kafka: {servidor_kafka} y BD: {servidor_bd}")

    def reconectar_bd(self):
        try:
            self.conexion_bd = conectar_bd(self.servidor_bd)
            return self.conexion_bd is not None
        except Exception as e:
            print(f"Error al reconectar BD: {e}")
            return False

    def verifico_driver(self, driver_id):
        if not self.reconectar_bd():
            print("No hay conexion a la BD")
            return False
        
        try:
            cursor = self.conexion_bd.cursor()
            consulta = "SELECT COUNT(*) FROM conductor WHERE id_conductor = %s"
            cursor.execute(consulta, (driver_id,))
            resultado = cursor.fetchone()
            cursor.close()
            if resultado[0] > 0:
                print(f"Conductor {driver_id} verificado en la Base de Datos.")
                return True
            else:
                print(f"Conductor {driver_id} NO verificado en la Base de Datos.")
                return False
            return 
        except Exception as e:
            print(f"Error al consultar el Conductor en la Base de Datos: {e}")
            return False

    def escuchar_peticiones_verificacion(self):
        consumidor = obtener_consumidor('conductor', 'central-verificaciones', self.servidor_kafka)
        print("CENTRAL: Escuchando peticiones de Verificación de Conductor...")

        for msg in consumidor:
            peticion = msg.value

            if peticion.get('type') == 'VERIFICAR_DRIVER':
                driver_id = peticion.get('driver_id')
                print(f"Verificando si el conductor {driver_id} esta registrado en la Base de Datos...")
                
                respuesta = {
                    'driver_id': driver_id,
                    'exists': self.verifico_driver(driver_id)
                }
                time.sleep(3)
                self.productor.send('respuestas_conductor', respuesta)
                self.productor.flush() # Aseguramos que el mensaje se envie
                print(f"Mensaje enviado al conductor: {driver_id}")

    def escuchar_peticiones_recarga(self):
        consumidor = obtener_consumidor('CARGA_SOLICITADA', 'central-recargas', self.servidor_kafka)
        print("CENTRAL: Escuchando peticiones de Recarga...")

        for msg in consumidor:
            peticion = msg.value

            if peticion.get('type') == 'SOLICITAR_RECARGA':
                driver_id = peticion.get('driver_id')
                cp_id = peticion.get('cp_id')
                print(f"El conductor: {driver_id} ha solicitado una recarga en el CP: {cp_id}")
                
                # AQUÍ IMPLEMENTAR LLAMADA A CP INDICADO PARA VER SI SE PUEDE REALIZAR LA RECARGA EN ESE CP
                with self._lock:
                    estado_cp = self.cps.get(cp_id, {}).get("estado", EST_DESC)

                if estado_cp == EST_ACTIVO:
                    cmd = {
                        "cp_id": cp_id,
                        "cmd": "INICIAR_CARGA",
                        "meta": {"driver_id": driver_id}
                    }
                    self.productor.send(TOPIC_COMANDOS, cmd)
                    self.productor.flush()

                    with self._lock:
                        self.cps.setdefault(cp_id, {})["estado"] = EST_SUM
                        self.driver_por_cp[cp_id] = driver_id
                        self.cp_por_driver[driver_id] = cp_id

                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "estado_carga": "recarga_autorizada",
                        "mensaje": f"CP {cp_id} disponible. Iniciando suministro..."
                    }
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga AUTORIZADA en {cp_id} para driver {driver_id}")
                    continue  # <- Evita ejecutar el bloque inferior de "confirmacion": True

                else:
                    # Denegar: responder al driver indicando el estado actual
                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "estado_carga": "recarga_denegada",
                        "mensaje": f"CP {cp_id} no disponible (estado actual: {estado_cp})."
                    }
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga DENEGADA en {cp_id} para driver {driver_id} (estado: {estado_cp})")


                # A PARTIR DE AQUÍ, DEVOLVEMOS LA RESPUESTA AL CONDUCTOR (EV_Driver)
                respuesta = {
                    'driver_id': driver_id,
                    'cp_id': cp_id,
                    'confirmacion': True
                }
                time.sleep(3)
                # NO TOCAR
                self.productor.send('respuestas_conductor', respuesta)
                self.productor.flush() # Aseguramos que el mensaje se envie
                print(f"Mensaje enviado al conductor: {driver_id}.")


    def escuchar_estados_cp(self):
        cons = obtener_consumidor(TOPIC_ESTADO, 'central-estados', self.servidor_kafka)
        print("[CENTRAL] Escuchando estado de CPs...")

        for msg in cons:
            st = msg.value
            cp_id  = st.get("cp_id")
            estado = st.get("estado")
            driver = st.get("driver_id")
            fin    = st.get("fin_carga", False)
            if not cp_id or not estado:
                continue

            with self._lock:
                info = self.cps.get(cp_id, {"estado": EST_DESC})
                info["estado"] = estado
                self.cps[cp_id] = info

            if fin and driver:
                ticket = {
                    "driver_id": driver,
                    "cp_id": cp_id,
                    "estado_carga": "recarga_finalizada",
                    "energia_kwh": st.get("energia_kwh"),
                    "importe_eur": st.get("importe_eur"),
                    "mensaje": f"Recarga finalizada en {cp_id}. Importe: {st.get('importe_eur')} €"
                }
                self.productor.send(TOPIC_RESP_DRIVER, ticket)
                self.productor.flush()
                print(f"[CENTRAL] Ticket enviado a driver {driver} (CP {cp_id}).")

                with self._lock:
                    self.driver_por_cp.pop(cp_id, None)
                    self.cp_por_driver.pop(driver, None)

    
    def consola_comandos(self):
        print("[CENTRAL] Comandos: PARAR <cp_id> | REANUDAR <cp_id> | PARAR_TODOS | ESTADO")
        while True:
            try:
                linea = input().strip()
            except EOFError:
                break

            if not linea:
                continue
            partes = linea.split()
            cmd = partes[0].upper()

            if cmd == "ESTADO":
                with self._lock:
                    print("\n[ESTADO DE TODOS LOS CPs]")
                    for cp_id, info in self.cps.items():
                        print(f"{cp_id}: {info.get('estado', EST_DESC)}")
                continue

            if cmd == "PARAR_TODOS":
                orden = {"cp_id": "ALL", "cmd": "PARAR"}
                self.productor.send(TOPIC_COMANDOS, orden)
                self.productor.flush()
                print("[CENTRAL] ORDEN PARAR enviada a todos los CPs.")
                continue

            if len(partes) < 2:
                print("Uso: PARAR <cp_id> | REANUDAR <cp_id> | PARAR_TODOS | ESTADO")
                continue

            cp_id = partes[1]
            if cmd not in ("PARAR", "REANUDAR"):
                print("Comando inválido. Usa: PARAR/REANUDAR/ESTADO/PARAR_TODOS")
                continue

            orden = {"cp_id": cp_id, "cmd": cmd}
            self.productor.send(TOPIC_COMANDOS, orden)
            self.productor.flush()
            print(f"[CENTRAL] ORDEN {cmd} enviada a {cp_id}")

    def procesar_linea_monitor(self, linea: str):
        partes = (linea or "").strip().split()
        if len(partes) < 2:
            print(f"[CENTRAL] Comando inválido del monitor: {linea!r}")
            return

        comando, cp_id = partes[0].upper(), partes[1]
        ahora = time.strftime("%H:%M:%S")

        with self._lock:
            self.cps.setdefault(cp_id, {"estado": EST_DESC})

            if comando == "AVISO":
                print(f"[{ahora}] [CENTRAL] Monitor avisa de {cp_id}. Estado actual: {self.cps[cp_id]['estado']}")
            elif comando == "MON_AVERIA":
                self.cps[cp_id]["estado"] = EST_AVERIA
                print(f"[{ahora}] [CENTRAL] {cp_id} -> AVERIA (reportado por monitor)")
            elif comando == "MON_RECUPERADO":
                self.cps[cp_id]["estado"] = EST_ACTIVO
                print(f"[{ahora}] [CENTRAL] {cp_id} -> ACTIVADO (monitor recuperado)")
            else:
                print(f"[CENTRAL] Comando de monitor NO reconocido: {linea!r}")

    def atender_monitor(self, cliente, direccion):
        try:
            with cliente:
                acumulador = b""
                while True:
                    datos = cliente.recv(1024)
                    if not datos:
                        break
                    acumulador += datos
                    while b"\n" in acumulador:
                        linea_bytes, acumulador = acumulador.split(b"\n", 1)
                        try:
                            linea = linea_bytes.decode(errors="ignore").strip()
                            if not linea:
                                continue
                            self._procesar_linea_monitor(linea)
                            cliente.sendall(b"ACK\n")
                        except Exception:
                            cliente.sendall(b"NACK\n")
        except Exception as e:
            print(f"[CENTRAL] Error con monitor {direccion}: {e}")


    def servidor_monitores(self, host_escucha="0.0.0.0", puerto_escucha=7001):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((host_escucha, puerto_escucha))
            servidor.listen(10)
            print(f"[CENTRAL] Escuchando monitores en {host_escucha}:{puerto_escucha}")
            while True:
                conn, addr = servidor.accept()
                threading.Thread(
                    target=self._atender_monitor,
                    args=(conn, addr),
                    daemon=True
                ).start()


    def iniciar_servicios(self): # Inicia los servicios en hilos separados
        print("Iniciando todos los servicios de la central...")
        
        # Crear hilos para cada tipo de mensaje
        hilo_verificaciones = threading.Thread(target=self.escuchar_peticiones_verificacion, daemon=True)
        hilo_cargas = threading.Thread(target=self.escuchar_peticiones_recarga, daemon=True)
        #hilo_registros = threading.Thread(target=self.escuchar_registros_cp, daemon=True)
        #hilo_estados = threading.Thread(target=self.escuchar_estados_cp, daemon=True)
        
        # Iniciar todos los hilos
        hilo_verificaciones.start()
        hilo_cargas.start()
        #hilo_registros.start()
        #hilo_estados.start()
        
        print("Todos los servicios iniciados. La central está operativa.")
        
        # Mantener el programa activo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nApagando central...")

def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Central.py <IP:puerto_broker> <IP:puerto_BD>")
        sys.exit(1) # Devuelve error
    
    servidor_kafka = sys.argv[1]
    servidor_bd = sys.argv[2]

    print(f"Kafka: {servidor_kafka}. BD: {servidor_bd}") # BORRRAR

    ev_central = EV_Central(servidor_kafka, servidor_bd)
    ev_central.iniciar_servicios()


if __name__ == "__main__":
    main()