from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import sys
import time
import mysql.connector
import socket
import os

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

def obtener_productor(servidor_kafka):
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka):
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id=grupo_id,
        auto_offset_reset='latest',
    )

def conectar_bd(servidor_bd):
    try:
        ip_bd, puerto_bd = servidor_bd.split(":")
        puerto_bd = int(puerto_bd)

        conexion = mysql.connector.connect(
            host=ip_bd,
            port=puerto_bd,
            user="sd_remoto",
            password="1234",
            database="evcharging"
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
        self.activo = True

        self._lock = threading.Lock()
        self._lock_bd = threading.Lock()  # Lock específico para operaciones BD
        self.driver_por_cp = {}
        self.cp_por_driver = {}

        self.conectar_bd_inicial()

        self.inicio = time.time()
        print(f"Central inicializada y conectada a Kafka: {servidor_kafka} y BD: {servidor_bd}")

    def conectar_bd_inicial(self):
        """Conexión inicial a BD"""
        try:
            self.conexion_bd = conectar_bd(self.servidor_bd)
            return self.conexion_bd is not None
        except Exception as e:
            print(f"Error en conexión inicial BD: {e}")
            return False

    def obtener_conexion_bd(self):
        """Obtiene una conexión válida a BD, reconectando si es necesario"""
        with self._lock_bd:
            try:
                # Verificar si la conexión existe y está viva
                if self.conexion_bd and self.conexion_bd.is_connected():
                    return self.conexion_bd
                else:
                    # Reconectar si no está conectada
                    print("Reconectando a BD...")
                    self.conexion_bd = conectar_bd(self.servidor_bd)
                    return self.conexion_bd
            except Exception as e:
                print(f"Error al obtener conexión BD: {e}")
                return None

    def ejecutar_consulta_bd(self, consulta, parametros=None, operacion="consulta"):
        """Ejecuta una consulta de forma segura manejando reconexiones"""
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print(f"No hay conexión a BD para {operacion}")
            return None
        
        try:
            cursor = conexion.cursor()
            cursor.execute(consulta, parametros or ())
            
            if operacion == "consulta":
                resultado = cursor.fetchall()
                cursor.close()
                return resultado
            else:  # inserción/actualización
                conexion.commit()
                cursor.close()
                return True
                
        except mysql.connector.Error as e:
            print(f"Error en {operacion} BD: {e}")
            # Intentar reconectar en caso de error
            try:
                self.conexion_bd = conectar_bd(self.servidor_bd)
            except:
                pass
            return None

    def verifico_driver(self, driver_id):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print("No hay conexion a la BD")
            return False
        
        try:
            cursor = conexion.cursor()
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
        except Exception as e:
            print(f"Error al consultar el Conductor en la Base de Datos: {e}")
            return False

    def verifico_cp(self, cp_id):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print("No hay conexion a la BD")
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT COUNT(*) FROM punto_recarga WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (cp_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            if resultado[0] > 0:
                print(f"Punto de Carga {cp_id} verificado en la Base de Datos.")
                return True
            else:
                print(f"Punto de Carga {cp_id} NO existente en la Base de Datos.")
                return False
        except Exception as e:
            print(f"Error al consultar el Punto de Carga en la Base de Datos: {e}")
            return False

    def existe_cp_en_bd(self, cp_id):
        """Verifica si un CP existe en la base de datos"""
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print("No hay conexión a la BD para verificar CP")
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT COUNT(*) FROM punto_recarga WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (cp_id,))
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] > 0
        except Exception as e:
            print(f"Error al verificar CP en BD: {e}")
            return False

    def registrar_cp_en_bd(self, cp_id, ubicacion, precio):
        """Registra un nuevo CP en la base de datos"""
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print("No hay conexión a la BD para registrar CP")
            return False
        
        try:
            cursor = conexion.cursor()
            
            # Verificar si ya existe
            if self.existe_cp_en_bd(cp_id):
                print(f"CP {cp_id} ya existe en BD, actualizando información...")
                consulta = """
                    UPDATE punto_recarga 
                    SET ubicacion_punto_recarga = %s, precio = %s, estado = 'DESCONECTADO'
                    WHERE id_punto_recarga = %s
                """
                cursor.execute(consulta, (ubicacion, precio, cp_id))
            else:
                print(f"Registrando nuevo CP {cp_id} en BD...")
                consulta = """
                    INSERT INTO punto_recarga (id_punto_recarga, id_central, ubicacion_punto_recarga, precio, estado) 
                    VALUES (%s, '0039051', %s, %s, 'DESCONECTADO')
                """
                cursor.execute(consulta, (cp_id, ubicacion, precio))
            
            conexion.commit()
            cursor.close()
            print(f"CP {cp_id} registrado/actualizado en BD correctamente")
            return True
        except Exception as e:
            print(f"Error al registrar CP en BD: {e}")
            return False

    def manejar_desconexion_cp(self, cp_id):
        print(f"[CENTRAL] Recibida desconexión del CP {cp_id}")
        
        with self._lock:
            if cp_id in self.cps:
                # Actualizar estado local
                self.cps[cp_id]["estado"] = EST_DESC
                self.cps[cp_id]["ultima_actualizacion"] = time.time()
                
                # Limpiar asignaciones si estaba en uso
                if cp_id in self.driver_por_cp:
                    driver_id = self.driver_por_cp[cp_id]
                    self.cp_por_driver.pop(driver_id, None)
                    self.driver_por_cp.pop(cp_id, None)
                    print(f"[CENTRAL] Limpiadas asignaciones del CP {cp_id} (driver: {driver_id})")
        
        # Actualizar base de datos
        self.actualizar_estado_cp_en_bd(cp_id, EST_DESC)
        print(f"[CENTRAL] CP {cp_id} marcado como DESCONECTADO")

    def actualizar_estado_cp_en_bd(self, cp_id, estado):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "UPDATE punto_recarga SET estado = %s WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (estado, cp_id))
            conexion.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al actualizar estado CP en BD: {e}")
            return False

    def obtener_cps_disponibles_bd(self): # Obtener CPs disponibles
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return []
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga, ubicacion_punto_recarga, precio FROM punto_recarga WHERE estado = 'ACTIVADO' ORDER BY id_punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados
        except Exception as e:
            print(f"Error al consultar CPs disponibles en BD: {e}")
            return []

    def escuchar_consultas_cps(self): # Para obtener los CPs disponibles y mandarlo al Driver
        consumidor = obtener_consumidor('consultas_cps', 'central-consultas', self.servidor_kafka)
        print("[CENTRAL] Escuchando consultas de CPs disponibles...")

        for msg in consumidor:
            consulta = msg.value
            
            if consulta.get('type') == 'CONSULTA_CPS_DISPONIBLES':
                driver_id = consulta.get('driver_id')
                consulta_id = consulta.get('consulta_id')
                print(f"[CENTRAL] Driver {driver_id} solicita CPs disponibles")
                
                # Obtener CPs disponibles de la BD
                cps_disponibles = self.obtener_cps_disponibles_bd()
                
                # Preparar respuesta
                respuesta = {
                    'type': 'RESPUESTA_CPS_DISPONIBLES',
                    'driver_id': driver_id,
                    'consulta_id': consulta_id,
                    'cps_disponibles': [
                        {
                            'cp_id': cp[0],
                            'ubicacion': cp[1],
                            'precio': float(cp[2])
                        }
                        for cp in cps_disponibles
                    ],
                    'timestamp': time.time()
                }
                
                # Enviar respuesta
                self.productor.send('respuestas_consultas_cps', respuesta)
                self.productor.flush()
                print(f"[CENTRAL] Enviados {len(cps_disponibles)} CPs disponibles a driver {driver_id}")

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
                self.productor.flush()
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
                
                cp_existe = self.verifico_cp(cp_id)

                if not cp_existe:
                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "confirmacion": False,
                        "mensaje": f"CP {cp_id} no disponible."
                    }
                    time.sleep(3)
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga DENEGADA en {cp_id} para driver {driver_id}")
                    continue

                with self._lock:
                    estado_cp = self.cps.get(cp_id, {}).get("estado", EST_DESC)
                    print(f"[CENTRAL] Estado del CP {cp_id}: {estado_cp}")

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
                        "confirmacion": True,
                        "mensaje": f"CP {cp_id} disponible. Iniciando suministro..."
                    }
                    time.sleep(3)
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga AUTORIZADA en {cp_id} para driver {driver_id}")
                
                else:
                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "confirmacion": False,
                        "mensaje": f"CP {cp_id} no disponible (estado actual: {estado_cp})."
                    }
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga DENEGADA en {cp_id} para driver {driver_id} (estado: {estado_cp})")

                print(f"Mensaje enviado al conductor: {driver_id}.")

    def escuchar_estados_cp(self):
        consumidor = obtener_consumidor(TOPIC_ESTADO, 'central-estados', self.servidor_kafka)
        print("[CENTRAL] Escuchando estados de CPs...")

        for msg in consumidor:
            estado_msg = msg.value
            cp_id = estado_msg.get("cp_id")
            estado = estado_msg.get("estado")
            
            if not cp_id or not estado:
                continue

            if estado_msg.get("tipo") == "DESCONEXION_CP":
                self.manejar_desconexion_cp(cp_id)
                continue

            print(f"[CENTRAL] Actualizando estado CP {cp_id}: {estado}")

            with self._lock:
                if cp_id not in self.cps:
                    self.cps[cp_id] = {}
                self.cps[cp_id]["estado"] = estado
                self.cps[cp_id]["ultima_actualizacion"] = time.time()

            self.actualizar_estado_cp_en_bd(cp_id, estado)

            if estado_msg.get("fin_carga", False):
                driver_id = estado_msg.get("driver_id")
                energia_kwh = estado_msg.get("energia_kwh", 0)
                importe_eur = estado_msg.get("importe_eur", 0)
                
                if driver_id:
                    ticket = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "estado_carga": "recarga_finalizada",
                        "energia_kwh": energia_kwh,
                        "importe_eur": importe_eur,
                        "mensaje": f"Recarga finalizada en {cp_id}. Energía: {energia_kwh:.2f} kWh, Importe: {importe_eur:.2f} €"
                    }
                    self.cps.setdefault(cp_id, {})["estado"] = EST_ACTIVO
                    self.productor.send(TOPIC_RESP_DRIVER, ticket)
                    self.productor.flush()
                    print(f"[CENTRAL] Ticket enviado a driver {driver_id} (CP {cp_id})")

                    with self._lock:
                        self.driver_por_cp.pop(cp_id, None)
                        self.cp_por_driver.pop(driver_id, None)

    def escuchar_registros_cp(self):
        consumidor = obtener_consumidor(TOPIC_REGISTROS, 'central-registros', self.servidor_kafka)
        print("[CENTRAL] Escuchando registros de CPs...")

        for msg in consumidor:
            registro = msg.value
            
            if registro.get('tipo') == 'REGISTRO_CP':
                cp_id = registro.get('cp_id')
                ubicacion = registro.get('ubicacion', 'N/A')
                precio = registro.get('precio_eur_kwh', 0.35)
                estado_inicial = registro.get('estado_inicial', EST_ACTIVO)
                
                print(f"[CENTRAL] Recibido registro de CP: {cp_id} en {ubicacion}")
                
                if self.registrar_cp_en_bd(cp_id, ubicacion, precio):
                    print(f"[CENTRAL] CP {cp_id} procesado en BD correctamente")
                else:
                    print(f"[CENTRAL] Error al procesar CP {cp_id} en BD")
                
                with self._lock:
                    if cp_id not in self.cps:
                        self.cps[cp_id] = {
                            "estado": estado_inicial,
                            "ubicacion": ubicacion,
                            "precio": precio,
                            "ultima_actualizacion": time.time()
                        }
                        print(f"[CENTRAL] Nuevo CP registrado: {cp_id} en {ubicacion} (estado: {estado_inicial})")
                    else:
                        self.cps[cp_id].update({
                            "ubicacion": ubicacion,
                            "precio": precio,
                            "ultima_actualizacion": time.time()
                        })
                        print(f"[CENTRAL] CP {cp_id} actualizado")
                
                self.actualizar_estado_cp_en_bd(cp_id, estado_inicial)
                
    def enviar_comando(self, cp_id, cmd):
        if cp_id == "ALL":
            for id_cp in self.cps.keys():
                orden = {"cp_id": id_cp, "cmd": cmd}
                self.productor.send(TOPIC_COMANDOS, orden)
                print(f"[CENTRAL] Comando {cmd} enviado a {id_cp}")
        else:
            orden = {"cp_id": cp_id, "cmd": cmd}
            self.productor.send(TOPIC_COMANDOS, orden)
            print(f"[CENTRAL] Comando {cmd} enviado a {cp_id}")
        
        self.productor.flush()

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
            elif comando == "HELLO":
                print(f"[{ahora}] [CENTRAL] Monitor avisa de {cp_id}. Estado actual: {self.cps[cp_id]['estado']} --> TODO OK")
            elif comando == "MON_AVERIA":
                if self.cps[cp_id]["estado"] != EST_DESC:
                    self.cps[cp_id]["estado"] = EST_AVERIA
                    print(f"[{ahora}] [CENTRAL] {cp_id} -> AVERIA (reportado por monitor)")
                    self.actualizar_estado_cp_en_bd(cp_id, EST_AVERIA)
                    orden = {"cp_id": cp_id, "cmd": "AVERIA"}
                    self.productor.send(TOPIC_COMANDOS, orden)
                    self.productor.flush()
                    print(f"[CENTRAL] Comando AVERIA enviado al CP {cp_id}")

            elif comando == "MON_RECUPERADO":
                self.cps[cp_id]["estado"] = EST_ACTIVO
                print(f"[{ahora}] [CENTRAL] {cp_id} -> ACTIVADO (monitor recuperado)")
                self.actualizar_estado_cp_en_bd(cp_id, EST_ACTIVO)
                orden = {"cp_id": cp_id, "cmd": "ACTIVADO"}
                self.productor.send(TOPIC_COMANDOS, orden)
                self.productor.flush()
                print(f"[CENTRAL] Comando resolucion de contingenica enviado al CP {cp_id}")
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
                            self.procesar_linea_monitor(linea)
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
                    target=self.atender_monitor,
                    args=(conn, addr),
                    daemon=True
                ).start()

    def iniciar_servicios(self):
        print("Iniciando todos los servicios de la central...")
        
        # Crear hilos para cada tipo de mensaje
        hilo_verificaciones = threading.Thread(target=self.escuchar_peticiones_verificacion, daemon=True)
        hilo_cargas = threading.Thread(target=self.escuchar_peticiones_recarga, daemon=True)
        hilo_registros = threading.Thread(target=self.escuchar_registros_cp, daemon=True)
        hilo_estados = threading.Thread(target=self.escuchar_estados_cp, daemon=True)
        hilo_monitores = threading.Thread(target=self.servidor_monitores, daemon=True)
        hilo_consultas = threading.Thread(target=self.escuchar_consultas_cps, daemon=True)
        
        # Iniciar todos los hilos
        hilo_verificaciones.start()
        hilo_cargas.start()
        hilo_registros.start()
        hilo_estados.start()
        hilo_monitores.start()
        hilo_consultas.start()
        
        print("Todos los servicios iniciados. La central está operativa.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nApagando central...")
    def mostrar_menu_central(self):
        try:
            while True:
                print("\n" + "="*60)
                print("          MENÚ DE CONTROL DE LA CENTRAL")
                print("="*60)
                print("1. Parar un CP específico")
                print("2. Parar todos los CPs")
                print("3. Reanudar un CP específico")
                print("4. Reanudar todos los CPs")
                print("5. Salir")
                print("="*60)

                opcion = input("Seleccione una opción (1-5): ").strip()

                if opcion == '1':
                    cp_id = input("Ingrese el ID del CP a PARAR: ").strip()
                    self.enviar_comando(cp_id, "PARAR")

                elif opcion == '2':
                    self.enviar_comando("ALL", "PARAR")

                elif opcion == '3':
                    cp_id = input("Ingrese el ID del CP a REANUDAR: ").strip()
                    self.enviar_comando(cp_id, "REANUDAR")

                elif opcion == '4':
                    self.enviar_comando("ALL", "REANUDAR")

                elif opcion == '5':
                    print("Saliendo del menú de la central...")
                    self.activo = False  # detener monitoreo
                    os._exit(0)
                    
                    break

                else:
                    print("Opción no válida. Intente de nuevo.")

        except KeyboardInterrupt:
            print("\nSaliendo del menú por interrupción...")
        except Exception as e:
            print(f"Error en el menú de la central: {e}")
    def iniciar_monitoreo_estados(self):
        def mostrar_estados_periodicamente():
            while self.activo:
                print("\n--- ESTADOS DE CPs ---")
                for cp_id, datos in self.cps.items():
                    estado = datos.get("estado", "N/A")
                    print(f"{cp_id}: {estado}")
                time.sleep(10)

        threading.Thread(target=mostrar_estados_periodicamente, daemon=True).start()

def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Central.py <IP:puerto_broker> <IP:puerto_BD>")
        sys.exit(1)
    
    servidor_kafka = sys.argv[1]
    servidor_bd = sys.argv[2]

    print(f"Kafka: {servidor_kafka}. BD: {servidor_bd}")

    ev_central = EV_Central(servidor_kafka, servidor_bd)
    ev_central.iniciar_monitoreo_estados()

    threading.Thread(target=ev_central.mostrar_menu_central, daemon=True).start()

    ev_central.iniciar_servicios()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Apagando central...")
        ev_central.activo = False
        os._exit(0)
if __name__ == "__main__":
    main()