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
        key_serializer=lambda k: k.encode('utf-8') if k else None,
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
        self._lock_bd = threading.Lock()
        self.driver_por_cp = {}
        self.cp_por_driver = {}

        self.conectar_bd_inicial()

        self.inicio = time.time()
        print(f"Central inicializada y conectada a Kafka: {servidor_kafka} y BD: {servidor_bd}")
        self.notificar_central_operativa()

    def notificar_central_operativa(self):
        print("[CENTRAL] Notificando a componentes que la central está operativa...")
        
        cps_bd = self.obtener_todos_cps_bd()
        for cp_id in cps_bd:
            mensaje_operativo = {
                "tipo": "CENTRAL_OPERATIVA",
                "cp_id": cp_id,
                "timestamp": time.time(),
                "mensaje": "La central está operativa nuevamente"
            }
            try:
                self.productor.send(f"comandos_cp_{cp_id}", mensaje_operativo)
                print(f"[CENTRAL] Notificación de operatividad enviada a CP {cp_id}")
            except Exception as e:
                print(f"[CENTRAL] Error al notificar operatividad a CP {cp_id}: {e}")

        mensaje_driver = {
            "tipo": "CENTRAL_OPERATIVA",
            "timestamp": time.time(),
            "mensaje": "La central está operativa nuevamente"
        }
        try:
            self.productor.send('respuestas_conductor', mensaje_driver)
            self.productor.send('respuestas_consultas_cps', mensaje_driver)
            print("[CENTRAL] Notificación de operatividad enviada a drivers")
        except Exception as e:
            print(f"[CENTRAL] Error al notificar operatividad a drivers: {e}")

        try:
            self.productor.flush(timeout=2.0)
            print("[CENTRAL] Todas las notificaciones de operatividad enviadas")
        except Exception as e:
            print(f"[CENTRAL] Error al hacer flush: {e}")

    def obtener_todos_cps_bd(self):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return []
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga FROM punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            return [cp[0] for cp in resultados]
        except Exception as e:
            print(f"Error al obtener CPs de BD: {e}")
            return []
    def conectar_bd_inicial(self):
        try:
            self.conexion_bd = conectar_bd(self.servidor_bd)
            return self.conexion_bd is not None
        except Exception as e:
            print(f"Error en conexión inicial BD: {e}")
            return False

    def obtener_conexion_bd(self):
        with self._lock_bd:
            try:
                if self.conexion_bd and self.conexion_bd.is_connected():
                    return self.conexion_bd
                else:
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
            else:
                conexion.commit()
                cursor.close()
                return True
                
        except mysql.connector.Error as e:
            print(f"Error en {operacion} BD: {e}")
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
        conexion = self.obtener_conexion_bd()
        if not conexion:
            print("No hay conexión a la BD para registrar CP")
            return False
        
        try:
            cursor = conexion.cursor()
            
            if self.existe_cp_en_bd(cp_id):
                print(f"CP {cp_id} ya existe en BD, actualizando información...")
                consulta = """
                    UPDATE punto_recarga 
                    SET ubicacion_punto_recarga = %s, precio = %s, estado = 'ACTIVADO'
                    WHERE id_punto_recarga = %s
                """
                cursor.execute(consulta, (ubicacion, precio, cp_id))
            else:
                print(f"Registrando nuevo CP {cp_id} en BD...")
                consulta = """
                    INSERT INTO punto_recarga (id_punto_recarga, id_central, ubicacion_punto_recarga, precio, estado) 
                    VALUES (%s, '0039051', %s, %s, 'ACTIVADO')
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
                self.cps[cp_id]["estado"] = EST_DESC
                self.cps[cp_id]["ultima_actualizacion"] = time.time()
                
                if cp_id in self.driver_por_cp:
                    driver_id = self.driver_por_cp[cp_id]
                    self.cp_por_driver.pop(driver_id, None)
                    self.driver_por_cp.pop(cp_id, None)
                    print(f"[CENTRAL] Limpiadas asignaciones del CP {cp_id} (driver: {driver_id})")
        
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

    def obtener_cps_disponibles_bd(self):
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

    def escuchar_consultas_cps(self):
        consumidor = obtener_consumidor('consultas_cps', 'central-consultas', self.servidor_kafka)
        print("[CENTRAL] Escuchando consultas de CPs disponibles...")

        for msg in consumidor:
            consulta = msg.value
            
            if consulta.get('type') == 'CONSULTA_CPS_DISPONIBLES':
                driver_id = consulta.get('driver_id')
                consulta_id = consulta.get('consulta_id')
                print(f"[CENTRAL] Driver {driver_id} solicita CPs disponibles")
                
                cps_disponibles = self.obtener_cps_disponibles_bd()
                
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
        try:
            print(f"[CENTRAL] Enviando comando '{cmd}' a '{cp_id}'")
            
            if cp_id == "ALL":
                cps_list = list(self.cps.keys())
                if not cps_list:
                    print("[CENTRAL] No hay CPs registrados para enviar comando")
                    return
                    
                print(f"[CENTRAL] Enviando a {len(cps_list)} CPs: {cps_list}")
                for id_cp in cps_list:
                    orden = {
                        "cp_id": id_cp, 
                        "cmd": cmd,
                        "timestamp": time.time()
                    }
                    topic_destino = f"comandos_cp_{id_cp}"
                    self.productor.send(topic_destino, value=orden)
                    print(f"[CENTRAL] Comando {cmd} enviado a CP {id_cp} en topic {topic_destino}")
            else:
                if cp_id not in self.cps:
                    print(f"[CENTRAL] CP {cp_id} no encontrado. CPs registrados: {list(self.cps.keys())}")
                    return
                    
                orden = {
                    "cp_id": cp_id, 
                    "cmd": cmd,
                    "timestamp": time.time()
                }
                topic_destino = f"comandos_cp_{cp_id}"
                self.productor.send(topic_destino, value=orden)
                print(f"[CENTRAL] Comando {cmd} enviado a CP {cp_id} en topic {topic_destino}")
            
            self.productor.flush()
            print(f"[CENTRAL] Flush completado para comando {cmd}")
            
        except Exception as e:
            print(f"[CENTRAL] ERROR al enviar comando: {e}")
            import traceback
            traceback.print_exc()

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
                    self.productor.send(f"comandos_cp_{cp_id}", orden)
                    self.productor.flush()
                    print(f"[CENTRAL] Comando AVERIA enviado al CP {cp_id}")

            elif comando == "MON_RECUPERADO":
                self.cps[cp_id]["estado"] = EST_ACTIVO
                print(f"[{ahora}] [CENTRAL] {cp_id} -> ACTIVADO (monitor recuperado)")
                self.actualizar_estado_cp_en_bd(cp_id, EST_ACTIVO)
                orden = {"cp_id": cp_id, "cmd": "ACTIVADO"}
                self.productor.send(f"comandos_cp_{cp_id}", orden)
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
        
        hilo_verificaciones = threading.Thread(target=self.escuchar_peticiones_verificacion, daemon=True)
        hilo_cargas = threading.Thread(target=self.escuchar_peticiones_recarga, daemon=True)
        hilo_registros = threading.Thread(target=self.escuchar_registros_cp, daemon=True)
        hilo_estados = threading.Thread(target=self.escuchar_estados_cp, daemon=True)
        hilo_monitores = threading.Thread(target=self.servidor_monitores, daemon=True)
        hilo_consultas = threading.Thread(target=self.escuchar_consultas_cps, daemon=True)
        
        hilo_verificaciones.start()
        hilo_cargas.start()
        hilo_registros.start()
        hilo_estados.start()
        hilo_monitores.start()
        hilo_consultas.start()
        
        print("Todos los servicios iniciados. La central está operativa.")
        
        try:
            while self.activo:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nApagando central...")

    def mostrar_menu_central(self):
        try:
            while self.activo:
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
                    if cp_id in self.cps:
                        self.enviar_comando(cp_id, "PARAR")
                    else:
                        print(f"CP {cp_id} no encontrado en central")

                elif opcion == '2':
                    if self.cps:
                        self.enviar_comando("ALL", "PARAR")
                    else:
                        print("No hay CPs registrados en la central")

                elif opcion == '3':
                    cp_id = input("Ingrese el ID del CP a REANUDAR: ").strip()
                    if cp_id in self.cps:
                        self.enviar_comando(cp_id, "REANUDAR")
                    else:
                        print(f"CP {cp_id} no encontrado en central")

                elif opcion == '4':
                    if self.cps:
                        self.enviar_comando("ALL", "REANUDAR")
                    else:
                        print("No hay CPs registrados en la central")

                elif opcion == '5':
                    print("Saliendo del menú de la central...")
                    self.activo = False
                    break

                else:
                    print("Opción no válida. Intente de nuevo.")

        except KeyboardInterrupt:
            print("\nSaliendo del menú por interrupción...")
        except Exception as e:
            print(f"Error en el menú de la central: {e}")

    def ver_cps_bd(self):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return {"total_cps": 0, "cps": []}
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga, estado FROM punto_recarga ORDER BY id_punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            
            cps_info = [
                {"id": cp[0], "estado": cp[1]}
                for cp in resultados
            ]
            
            info_completa = {
                "total_cps": len(resultados),
                "cps": cps_info
            }
            
            COLOR_RESET = "\033[0m"
            COLOR_VERDE = "\033[92m"
            COLOR_NARANJA = "\033[93m"
            COLOR_ROJO = "\033[91m"
            COLOR_GRIS = "\033[90m"
            
            print(f"[BD] Encontrados {info_completa['total_cps']} CPs en la base de datos")
            
            for cp in cps_info:
                estado = cp["estado"]
                color = COLOR_RESET
                
                if estado == "ACTIVADO":
                    color = COLOR_VERDE
                elif estado == "PARADO":
                    color = COLOR_NARANJA
                elif estado == "SUMINISTRANDO":
                    color = COLOR_VERDE
                elif estado == "AVERIA":
                    color = COLOR_ROJO
                elif estado == "DESCONECTADO":
                    color = COLOR_GRIS
                
                print(f"ID: {cp['id']}, ESTADO: {color}\"{estado}\"{COLOR_RESET}")
                
            return info_completa
            
        except Exception as e:
            print(f"Error al obtener información de CPs en BD: {e}")
            return {"total_cps": 0, "cps": []}

    def iniciar_monitoreo_estados(self):
        def mostrar_estados_periodicamente():
            COLOR_RESET = "\033[0m"
            COLOR_VERDE = "\033[92m"
            COLOR_NARANJA = "\033[93m"
            COLOR_ROJO = "\033[91m"
            COLOR_GRIS = "\033[90m"

            while self.activo:
                print("\n" + "="*50)
                print("          ESTADOS ACTUALES DE CPs")
                print("="*50)
                
                self.ver_cps_bd()
                time.sleep(2)
                print("-" * 50)
                print("          ESTADOS EN MEMORIA DE LA CENTRAL")
                print("-" * 50)

                if not self.cps:
                    print("No hay CPs conectados con la central")
                else:
                    for cp_id, datos in self.cps.items():
                        estado = datos.get("estado", "N/A")
                        ubicacion = datos.get("ubicacion", "N/A")
                        color = COLOR_RESET
                        icono = "⚡"

                        if estado == "ACTIVADO":
                            color = COLOR_VERDE
                            icono = "✅"
                        elif estado == "PARADO":
                            color = COLOR_NARANJA
                            icono = "⏸️"
                        elif estado == "SUMINISTRANDO":
                            color = COLOR_VERDE
                            icono = "🔌"
                        elif estado == "AVERIA":
                            color = COLOR_ROJO
                            icono = "🚨"
                        elif estado == "DESCONECTADO":
                            color = COLOR_GRIS
                            icono = "🔌"

                        print(f"{icono} {color}{cp_id}: {estado} - {ubicacion}{COLOR_RESET}")
                
                print("="*50)
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
    time.sleep(3)

    def notificar_desconexion_central():
        """Notifica a todos los componentes que la central se está desconectando"""
        print("\n🔴 [CENTRAL] Notificando desconexión a todos los componentes...")
        
        # Notificar a todos los CPs registrados
        for cp_id in ev_central.cps.keys():
            mensaje_desconexion = {
                "tipo": "DESCONEXION_CENTRAL",
                "cp_id": cp_id,
                "timestamp": time.time(),
                "mensaje": "La central se está desconectando. Espere a que vuelva a estar operativa."
            }
            try:
                ev_central.productor.send(f"comandos_cp_{cp_id}", mensaje_desconexion)
                print(f"✅ [CENTRAL] Notificación enviada a CP {cp_id}")
            except Exception as e:
                print(f"❌ [CENTRAL] Error al notificar a CP {cp_id}: {e}")
        
        # Notificar a todos los drivers (topic general)
        mensaje_driver = {
            "tipo": "DESCONEXION_CENTRAL",
            "timestamp": time.time(),
            "mensaje": "La central se está desconectando. Espere a que vuelva a estar operativa."
        }
        try:
            ev_central.productor.send('respuestas_conductor', mensaje_driver)
            ev_central.productor.send('respuestas_consultas_cps', mensaje_driver)
            print("✅ [CENTRAL] Notificación enviada a drivers")
        except Exception as e:
            print(f"❌ [CENTRAL] Error al notificar a drivers: {e}")
        
        # Esperar a que los mensajes se envíen
        try:
            ev_central.productor.flush(timeout=2.0)
            print("✅ [CENTRAL] Todos los mensajes de desconexión enviados")
        except Exception as e:
            print(f"❌ [CENTRAL] Error al hacer flush: {e}")

    # Crear hilo del menú (no daemon para que no se cierre abruptamente)
    hilo_menu = threading.Thread(target=ev_central.mostrar_menu_central)
    hilo_menu.start()

    try:
        # Iniciar servicios
        ev_central.iniciar_servicios()
        
        # Esperar a que el hilo del menú termine
        hilo_menu.join()
        notificar_desconexion_central()
        print("\n🔴 Cerrando central...")
        ev_central.activo = False  # Detener todos los servicios
        
        # Dar tiempo para que los servicios se cierren correctamente
        time.sleep(2)
        
        print("✅ Central cerrada correctamente")
        
    except KeyboardInterrupt:
        print("\n🔴 Interrupción recibida. Cerrando central...")
        
        # Notificar desconexión antes de cerrar
        notificar_desconexion_central()
        
        ev_central.activo = False
        time.sleep(2)
        print("✅ Central cerrada correctamente")
    
    # ✅ SALIR DEL PROGRAMA
    sys.exit(0)

if __name__ == "__main__":
    main()