from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import sys
import time
import mysql.connector
import socket
import os
import secrets
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# TOPICS
TOPIC_REGISTROS = "registros_cp"
TOPIC_COMANDOS  = "comandos_cp"
TOPIC_ESTADO    = "estado_cp"
TOPIC_RESP_DRIVER = "respuestas_conductor"
TOPIC_SOLICITUD   = "CARGA_SOLICITADA"
TOPIC_VERIF       = "conductor"
TOPIC_CAMBIOS_ESTADO_DRIVER = "cambios_estado_driver"

# ESTADOS CP
EST_ACTIVO = "ACTIVADO"
EST_PARADO = "PARADO"
EST_AVERIA = "AVERIA"
EST_SUM    = "SUMINISTRANDO"
EST_DESC   = "DESCONECTADO"

def obtener_productor(servidor_kafka): # Obtener productor Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka): # Obtener consumidor Kafka
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id=grupo_id,
        auto_offset_reset='latest',
    )

def conectar_bd(servidor_bd): # Conectar a la BD
    try:
        ip_bd, puerto_bd = servidor_bd.split(":")
        puerto_bd = int(puerto_bd)

        conexion = mysql.connector.connect( # Parametros de conexión
            host=ip_bd,
            port=puerto_bd,
            user="sd_remoto",
            password="1234",
            database="evcharging",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            connection_timeout=10,
            pool_size=5,
            pool_reset_session=True
        )

        print(f"Servidor conectado a la Base de Datos en {servidor_bd}") # Si la conexión es exitosa
        cur = conexion.cursor()
        cur.execute("SELECT DATABASE()")
        print("[CENTRAL] DATABASE():", cur.fetchone())
        cur.execute("SELECT COUNT(*) FROM punto_recarga")
        print("[CENTRAL] Nº filas punto_recarga:", cur.fetchone())
        cur.close()

        return conexion
    except Exception as e:
        print(f"Error al conectar a la Base de Datos: {e}")
        return None
    
class EV_Central: # Clase Central (Principal para la práctica)
    def __init__(self, servidor_kafka, servidor_bd): # Inicializamos los parámetros de la central
        self.servidor_kafka = servidor_kafka
        self.servidor_bd = servidor_bd
        self.productor = obtener_productor(servidor_kafka)
        self.cps = {} # Para almacenar los CPs
        self.activo = True
        
        self._lock = threading.Lock() # Sincronización de hilos
        self.driver_por_cp = {}
        self.cp_por_driver = {}

        # Test de conexión inicial a BD
        conexion_test = self.obtener_conexion_bd()
        if conexion_test: # Si la conexión es exitosa
            print(f"Test de conexión BD exitoso")
            conexion_test.close()
        else: # Si falla la conexión
            print("No se pudo conectar a BD inicialmente")

        self.inicio = time.time()
        print(f"Central inicializada y conectada a Kafka: {servidor_kafka}")
        self.notificar_central_operativa() # Notificar que la central está operativa
    def _get_key_hex(self, cp_id: str):
        return (self.cps.get(str(cp_id)) or {}).get("clave_simetrica")

    def _encrypt_for_cp(self, cp_id: str, payload: dict) -> dict:
        clave_hex = self._get_key_hex(cp_id)
        if not clave_hex:
            raise RuntimeError(f"CP {cp_id} sin clave en memoria (REAUTH requerido)")

        key = bytes.fromhex(clave_hex)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        pt = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        ct = aesgcm.encrypt(nonce, pt, None)

        wrapper = {
            "cp_id": str(cp_id),
            "alg": "AESGCM",
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "enc": base64.b64encode(ct).decode("ascii")
        }

        # PRINT: confirmación de cifrado
        info = payload.get("cmd") or payload.get("tipo") or payload.get("estado") or "N/A"
        print(f"[CENTRAL][CRYPTO] CIFRADO -> CP {cp_id} info={info} nonce_len={len(wrapper['nonce'])} enc_len={len(wrapper['enc'])}")

        return wrapper


    def _decrypt_from_cp(self, wrapper: dict) -> dict:
        cp_id = str(wrapper.get("cp_id"))
        clave_hex = self._get_key_hex(cp_id)
        if not clave_hex:
            raise RuntimeError(f"CP {cp_id} sin clave en memoria (REAUTH requerido)")

        key = bytes.fromhex(clave_hex)
        aesgcm = AESGCM(key)
        nonce = base64.b64decode(wrapper["nonce"])
        ct = base64.b64decode(wrapper["enc"])
        pt = aesgcm.decrypt(nonce, ct, None)

        obj = json.loads(pt.decode("utf-8"))

        #PRINT: confirmación de descifrado
        info = obj.get("cmd") or obj.get("tipo") or obj.get("estado") or "N/A"
        print(f"[CENTRAL][CRYPTO] DESCIFRADO <- CP {cp_id} info={info} keys={list(obj.keys())}")

        return obj
    
    def notificar_central_operativa(self): # Notificar a CPs y drivers que la central está operativa
        print("[CENTRAL] Notificando a componentes que la central está operativa...")
        
        # Notificar a todos los CPs registrados en BD
        cps_bd = self.obtener_todos_cps_bd()
        for cp_id in cps_bd:
            mensaje_operativo = { # Creamos el mensaje para enviar a cada CP
                "tipo": "CENTRAL_OPERATIVA",
                "cp_id": cp_id,
                "timestamp": time.time(),
                "mensaje": "La central está operativa nuevamente"
            }
            try:
                self.productor.send(f"comandos_cp_{cp_id}", mensaje_operativo) # Enviamos el mensaje al topic del CP
                print(f"[CENTRAL] Notificación de operatividad enviada a CP {cp_id}")
            except Exception as e:
                print(f"[CENTRAL] Error al notificar operatividad a CP {cp_id}: {e}")
        
        # Notificar a todos los drivers (topic general)
        mensaje_driver = { # Creamos el mensaje para enviar a los drivers
            "tipo": "CENTRAL_OPERATIVA",
            "timestamp": time.time(),
            "mensaje": "La central está operativa nuevamente"
        }
        try:
            self.productor.send('respuestas_conductor', mensaje_driver) # Enviamos el mensaje al topic de drivers
            self.productor.send('respuestas_consultas_cps', mensaje_driver)
            print("[CENTRAL] Notificación de operatividad enviada a drivers")
        except Exception as e:
            print(f"[CENTRAL] Error al notificar operatividad a drivers: {e}")
        
        # Esperar a que los mensajes se envíen
        try:
            self.productor.flush(timeout=2.0)
            print("[CENTRAL] Todas las notificaciones de operatividad enviadas")
        except Exception as e:
            print(f"[CENTRAL] Error al hacer flush: {e}")

    def obtener_todos_cps_bd(self): # Obtener todos los CPs registrados en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion:
            return []
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga FROM punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()  # Cerrar conexión después de usar
            return [cp[0] for cp in resultados]
        except Exception as e: # Si hay un error
            print(f"Error al obtener CPs de BD: {e}")
            try:
                conexion.close()
            except:
                pass
            return []
        
    def obtener_conexion_bd(self): # Obtener nueva conexión a BD ara cada operación
        try:
            return conectar_bd(self.servidor_bd)
        except Exception as e:
            print(f"Error al crear nueva conexión BD: {e}")
            return None

    def verifico_driver(self, driver_id): # Verificar si un driver existe en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            print("No hay conexion a la BD")
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT COUNT(*) FROM conductor WHERE id_conductor = %s"
            cursor.execute(consulta, (driver_id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if resultado[0] > 0: # Si el conductor existe
                print(f"Conductor {driver_id} verificado en la Base de Datos.")
                return True
            else: # Si no existe
                print(f"Conductor {driver_id} NO verificado en la Base de Datos.")
                return False
        except Exception as e: # Si ocurre un error
            print(f"Error al consultar el Conductor en la Base de Datos: {e}")
            conexion.close()
            return False

    def verifico_cp(self, cp_id): # Verificar si un cp existe en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            print("No hay conexion a la BD")
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT COUNT(*) FROM punto_recarga WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (cp_id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if resultado[0] > 0: # Si el cp existe
                print(f"Punto de Carga {cp_id} verificado en la Base de Datos.")
                return True
            else: # Si no existe
                print(f"Punto de Carga {cp_id} NO existente en la Base de Datos.")
                return False
        except Exception as e: # Si ocurre un error
            print(f"Error al consultar el Punto de Carga en la Base de Datos: {e}")
            conexion.close()
            return False

    def registrar_cp_en_bd(self, cp_id, ubicacion, precio): # Registrar un nuevo CP en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            print("No hay conexión a la BD para registrar CP")
            return False
        
        try: # Si hay conexión, intento registrar el CP
            cursor = conexion.cursor()
            
            # Verificar si ya existe
            if self.verifico_cp(cp_id): # Si ya existe, actualizo
                print(f"CP {cp_id} ya existe en BD, actualizando información...")
                consulta = "UPDATE punto_recarga SET ubicacion_punto_recarga = %s, precio = %s, estado = 'ACTIVADO' WHERE id_punto_recarga = %s"
                cursor.execute(consulta, (ubicacion, precio, cp_id))
            else: # Si no existe, inserto
                print(f"Registrando nuevo CP {cp_id} en BD...")
                consulta = "INSERT INTO punto_recarga (id_punto_recarga, id_central, ubicacion_punto_recarga, precio, estado) VALUES (%s, '0039051', %s, %s, 'ACTIVADO')"
                cursor.execute(consulta, (cp_id, ubicacion, precio))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"CP {cp_id} registrado/actualizado en BD correctamente")
            return True
        except Exception as e: # Si ocurre un error
            print(f"Error al registrar CP en BD: {e}")
            conexion.close()
            return False

    def manejar_desconexion_cp(self, cp_id): # Manejar desconexión de un CP
        print(f"[CENTRAL] Recibida desconexión del CP {cp_id}")
        
        with self._lock: # Bloqueo para sincronización
            if cp_id in self.cps: # Si el CP está registrado
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

    def actualizar_estado_cp_en_bd(self, cp_id, estado): # Actualizar estado de un CP en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            return False
        
        try: # Si hay conexión, intento actualizar el estado
            cursor = conexion.cursor()
            consulta = "UPDATE punto_recarga SET estado = %s WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (estado, cp_id))
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Exception as e: # Si ocurre un error
            print(f"Error al actualizar estado CP en BD: {e}")
            conexion.close()
            return False


    def validar_cp_en_bd(self, cp_id: str, credencial: str) -> bool:
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return False
        try:
            cur = conexion.cursor()
            cur.execute("""
                SELECT 1
                FROM punto_recarga
                WHERE id_punto_recarga = %s
                AND credencial = %s
                AND activo = 1
                LIMIT 1
            """, (cp_id, credencial))
            ok = cur.fetchone() is not None
            cur.close()
            conexion.close()
            return ok
        except Exception as e:
            print(f"[CENTRAL] Error validando CP en BD: {e}")
            try: conexion.close()
            except: pass
            return False




    def marcar_cp_con_clave(self, cp_id: str):
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return

        try:
            cur = conexion.cursor()
            cur.execute("""
                UPDATE punto_recarga
                SET tiene_clave_simetrica = 1
                WHERE id_punto_recarga = %s
            """, (cp_id,))
            conexion.commit()
            cur.close()
            conexion.close()
        except Exception as e:
            print(f"[CENTRAL] No se pudo marcar tiene_clave_simetrica: {e}")
            try:    
                conexion.close()
            except:
                pass



    def obtener_cps_disponibles_bd(self): # Obtener CPs disponibles
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            return [] # devuelvo lista vacía
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga, ubicacion_punto_recarga, precio FROM punto_recarga WHERE estado = 'ACTIVADO' ORDER BY id_punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()
            return resultados
        except Exception as e: # Si ocurre un error
            print(f"Error al consultar CPs disponibles en BD: {e}")
            conexion.close()
            return [] # devuelvo lista vacía

    def escuchar_consultas_cps(self): # Para obtener los CPs disponibles y mandarlo al Driver
        consumidor = obtener_consumidor('consultas_cps', 'central-consultas', self.servidor_kafka) # Consumidor Kafka con topic 'consultas_cps'
        print("[CENTRAL] Escuchando consultas de CPs disponibles...")

        for msg in consumidor: # Bucle para escuchar mensajes
            consulta = msg.value # Guardo el valor del mensaje
            
            if consulta.get('type') == 'CONSULTA_CPS_DISPONIBLES': # Si el tipo es: 'CONSULTA_CPS_DISPONIBLES'
                driver_id = consulta.get('driver_id') # Guardi el driver_id
                consulta_id = consulta.get('consulta_id')
                print(f"[CENTRAL] Driver {driver_id} solicita CPs disponibles")
                
                # Obtener CPs disponibles de la BD
                cps_disponibles = self.obtener_cps_disponibles_bd()
                
                # Preparar respuesta
                respuesta = {
                    'type': 'RESPUESTA_CPS_DISPONIBLES',
                    'driver_id': driver_id,
                    'consulta_id': consulta_id,
                    'cps_disponibles': [{'cp_id': cp[0], 'ubicacion': cp[1], 'precio': float(cp[2])} for cp in cps_disponibles], 'timestamp': time.time()
                }
                
                # Enviar respuesta al driver
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
                
                existe = self.verifico_driver(driver_id)
                
                if existe:
                    # Cuando el driver se verifica, cambiar estado a "Activo"
                    self.actualizar_estado_driver(driver_id, "Activo")
                    # Registrar en auditoría
                    self.registrar_auditoria(f"Driver-{driver_id}", "login_driver", f"Driver {driver_id} se ha logueado correctamente")
                
                respuesta = {
                    'driver_id': driver_id,
                    'exists': existe
                }
                time.sleep(3)
                self.productor.send('respuestas_conductor', respuesta)
                self.productor.flush()
                print(f"Mensaje enviado al conductor: {driver_id}")

    def sincronizar_estado_cp_desde_bd(self, cp_id):
        datos_cp = self.obtener_estado_cp_bd(cp_id)
        
        if datos_cp:
            with self._lock:
                if cp_id not in self.cps:
                    self.cps[cp_id] = {}
                
                estado_anterior = self.cps[cp_id].get("estado", "N/A")
                estado_nuevo = datos_cp["estado"]
                
                # Actualizar en memoria
                self.cps[cp_id]["estado"] = estado_nuevo
                self.cps[cp_id]["temperatura"] = datos_cp["temperatura"]
                self.cps[cp_id]["ultima_actualizacion"] = time.time()
                
                if estado_anterior != estado_nuevo:
                    print(f"[CENTRAL] Estado sincronizado CP {cp_id}: {estado_anterior} → {estado_nuevo}")
                    
                    # Si pasa de PARADO a ACTIVADO, limpiar asignaciones si las hubiera
                    if estado_anterior == "PARADO" and estado_nuevo == "ACTIVADO":
                        if cp_id in self.driver_por_cp:
                            driver_id = self.driver_por_cp[cp_id]
                            print(f"[CENTRAL] Limpiando asignación obsoleta: CP {cp_id} - Driver {driver_id}")
                            self.cp_por_driver.pop(driver_id, None)
                            self.driver_por_cp.pop(cp_id, None)
            
            return True
        return False

    def obtener_estado_cp_bd(self, cp_id):
        """Obtener estado actual de un CP desde la base de datos"""
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return None
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT estado, temperatura FROM punto_recarga WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (cp_id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if resultado:
                return {
                    "estado": resultado[0],
                    "temperatura": resultado[1] if resultado[1] is not None else 20
                }
            return None
        except Exception as e:
            print(f"Error al obtener estado CP desde BD: {e}")
            conexion.close()
            return None

    def obtener_temperatura_cp(self, cp_id):
        """Obtener temperatura actual de un CP"""
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return None
        
        try:
            cursor = conexion.cursor()
            consulta = "SELECT temperatura FROM punto_recarga WHERE id_punto_recarga = %s"
            cursor.execute(consulta, (cp_id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error al obtener temperatura CP: {e}")
            conexion.close()
            return None

    def verificar_disponibilidad_cp(self, cp_id, estado_cp, temperatura): # Verificar disponibilidad del CP
        
        # 1. Verificar estado básico
        if estado_cp == EST_DESC:
            return False, "CP desconectado"
        elif estado_cp == EST_AVERIA:
            return False, "CP en avería"
        elif estado_cp == EST_SUM:
            return False, "CP ya está suministrando"
        elif estado_cp == "PARADO":
            # Verificar si está parado por alerta meteorológica
            if temperatura is not None and temperatura < 0:
                return False, f"Alerta meteorológica ({temperatura}°C)"
            else:
                # Si está PARADO pero temperatura >= 0, puede ser un estado temporal
                # Verificar en BD para asegurar
                datos_bd = self.obtener_estado_cp_bd(cp_id)
                if datos_bd and datos_bd["estado"] == "PARADO":
                    return False, "CP parado manualmente"
                else:
                    # Estado inconsistente, forzar sincronización
                    self.sincronizar_estado_cp_desde_bd(cp_id)
                    with self._lock:
                        estado_cp = self.cps.get(cp_id, {}).get("estado", EST_DESC)
                    
                    if estado_cp == "ACTIVADO":
                        return True, "CP disponible (estado corregido)"
                    else:
                        return False, f"Estado {estado_cp}"
        
        # 2. Verificar temperatura si estado es ACTIVADO
        elif estado_cp == EST_ACTIVO:
            if temperatura is not None and temperatura < 0:
                # Estado inconsistente: ACTIVADO pero temperatura < 0
                print(f"[CENTRAL] ERROR: CP {cp_id} ACTIVADO pero temperatura {temperatura}°C")
                # Actualizar estado a PARADO
                self.actualizar_estado_cp_en_bd(cp_id, "PARADO")
                with self._lock:
                    self.cps[cp_id]["estado"] = "PARADO"
                return False, f"Alerta meteorológica detectada ({temperatura}°C)"
            else:
                return True, "CP disponible"
        
        # 3. Estado desconocido
        else:
            return False, f"Estado desconocido: {estado_cp}"

    def escuchar_peticiones_recarga(self):
        consumidor = obtener_consumidor('CARGA_SOLICITADA', 'central-recargas', self.servidor_kafka)
        print("CENTRAL: Escuchando peticiones de Recarga...")

        for msg in consumidor:
            peticion = msg.value

            if peticion.get('type') == 'SOLICITAR_RECARGA':
                driver_id = peticion.get('driver_id')
                cp_id = peticion.get('cp_id')
                
                # REGISTRAR EN AUDITORÍA: Driver solicita suministro
                self.registrar_auditoria(f"Driver-{driver_id}", "solicitud_carga",
                                        f"Driver {driver_id} solicitando suministro en CP {cp_id}")
                
                print(f"El conductor: {driver_id} ha solicitado una recarga en el CP: {cp_id}")
                
                # 1. Sincronizar estado desde BD ANTES de verificar
                self.sincronizar_estado_cp_desde_bd(cp_id)
                
                cp_existe = self.verifico_cp(cp_id)

                if not cp_existe:
                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "confirmacion": False,
                        "mensaje": f"CP {cp_id} no disponible."
                    }
                    # REGISTRAR EN AUDITORÍA: Solicitud denegada
                    self.registrar_auditoria("CENTRAL", "carga_denegada", f"Solicitud de carga denegada para el Driver {driver_id} en CP {cp_id}")
                    time.sleep(3)
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga DENEGADA en {cp_id} para driver {driver_id}")
                    continue

                # 2. Obtener estado sincronizado
                with self._lock:
                    estado_cp = self.cps.get(cp_id, {}).get("estado", EST_DESC)
                    temperatura = self.cps.get(cp_id, {}).get("temperatura", 20)
                
                print(f"[CENTRAL] Estado CP {cp_id} después de sincronizar: {estado_cp}, Temp: {temperatura}°C")

                # 3. Verificar disponibilidad CORRECTAMENTE
                disponible, motivo = self.verificar_disponibilidad_cp(cp_id, estado_cp, temperatura)
                
                if not disponible:
                    resp = {
                        "driver_id": driver_id,
                        "cp_id": cp_id,
                        "confirmacion": False,
                        "mensaje": f"CP {cp_id} no disponible: {motivo}"
                    }
                    # REGISTRAR EN AUDITORÍA: Solicitud denegada
                    self.registrar_auditoria("CENTRAL", "carga_denegada",
                                            f"Solicitud de carga denegada para el Driver {driver_id} en CP {cp_id} - {motivo}")
                    self.productor.send(TOPIC_RESP_DRIVER, resp)
                    self.productor.flush()
                    print(f"[CENTRAL] Recarga DENEGADA en {cp_id} para driver {driver_id}: {motivo}")
                    continue

                # 4. Si está disponible, proceder
                # Cambiar estado del driver a "Esperando a CP X"
                self.actualizar_estado_driver(driver_id, f"Esperando a CP {cp_id}")
                
                cmd = {
                    "cp_id": cp_id,
                    "cmd": "INICIAR_CARGA",
                    "meta": {"driver_id": driver_id}
                }
                topic_destino = f"comandos_cp_{cp_id}"
                payload = self._encrypt_for_cp(cp_id, cmd)
                self.productor.send(topic_destino, value=payload)
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
                # REGISTRAR EN AUDITORÍA: Suministro concedido
                self.registrar_auditoria("CENTRAL", "suministro_concedido",
                                        f"Suministro concedido para Driver {driver_id} en CP {cp_id}")
                time.sleep(3)
                self.productor.send(TOPIC_RESP_DRIVER, resp)
                self.productor.flush()
                print(f"[CENTRAL] Recarga AUTORIZADA en {cp_id} para driver {driver_id}")

                print(f"Mensaje enviado al conductor: {driver_id}.")

    def escuchar_estados_cp(self):
        consumidor = obtener_consumidor(TOPIC_ESTADO, 'central-estados', self.servidor_kafka)
        print("[CENTRAL] Escuchando estados de CPs...")

        for msg in consumidor:
            raw = msg.value

            # Si viene cifrado (wrapper con nonce/enc)
            if isinstance(raw, dict) and "enc" in raw and "nonce" in raw:
                print("[CENTRAL] Recibido wrapper cifrado (cp_id):", raw.get("cp_id"))
                try:
                    estado_msg = self._decrypt_from_cp(raw)
                    print("[CENTRAL] Descifrado OK:", estado_msg)
                except Exception as e:
                    print(f"[CENTRAL] ERROR descifrando estado CP: {e}")
                    continue
            else:
                # compatibilidad temporal si aún llega en claro
                estado_msg = raw

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

                    # REGISTRAR EN AUDITORÍA: Fin del suministro
                    self.registrar_auditoria(f"CP-{cp_id}", "fin_suministro",
                                            f"Fin del suministro del Driver {driver_id} en el CP {cp_id}")

                    # Cambiar estado del driver a "Activo"
                    self.actualizar_estado_driver(driver_id, "Activo")

                    with self._lock:
                        self.driver_por_cp.pop(cp_id, None)
                        self.cp_por_driver.pop(driver_id, None)


    def escuchar_registros_cp(self): # Escuchar registros de nuevos CPs 
        consumidor = obtener_consumidor(TOPIC_REGISTROS, 'central-registros', self.servidor_kafka) # Consumidor Kafka con topic 'registros_cp' 
        print("[CENTRAL] Escuchando registros de CPs...") 
        for msg in consumidor: # Bucle para escuchar mensajes 
            registro = msg.value
            if registro.get('tipo') == 'REGISTRO_CP': 
                cp_id = str(registro.get('cp_id')) 
                ubicacion = registro.get('ubicacion', 'N/A') 
                precio = registro.get('precio_eur_kwh', 0.35) 
                estado_inicial = registro.get('estado_inicial', EST_ACTIVO) 
                print(f"[CENTRAL] Recibido registro de CP (Engine): {cp_id} en {ubicacion}") 
                # Si no existe en BD, NO insertamos desde Central. 
                if not self.verifico_cp(cp_id): 
                    print(f"[CENTRAL] CP {cp_id} aún NO está en BD (EV_Registry). Ignorando REGISTRO_CP del Engine.") 
                    continue # <-- si estás dentro del bucle de consumo Kafka 
                with self._lock: 
                    if cp_id not in self.cps: 
                        self.cps[cp_id] = { 
                            "estado": estado_inicial, 
                            "ubicacion": ubicacion, 
                            "precio": precio, 
                            "ultima_actualizacion": time.time() 
                            } 
                        print(f"[CENTRAL] CP {cp_id} cargado en memoria (ya existía en BD).") 
                    else: 
                        self.cps[cp_id].update({ 
                            "ubicacion": ubicacion, 
                            "precio": precio, 
                            "ultima_actualizacion": time.time() 
                            }) 
                        print(f"[CENTRAL] CP {cp_id} memoria actualizada (ya existía en BD).")

    def enviar_comando(self, cp_id, cmd): # Enviar comando a un CP específico o a todos
        try: # Intento enviar el comando
            print(f"[CENTRAL] Enviando comando '{cmd}' a '{cp_id}'")
            
            if cp_id == "ALL": # Si es para todos los CPs
                cps_list = list(self.cps.keys()) # Obtengo la lista de todos los CPs registrados
                if not cps_list: # Si no hay CPs registrados, envío ensaje
                    print("[CENTRAL] No hay CPs registrados para enviar comando")
                    return
                
                # si hay CPs, envío el comando a cada uno
                print(f"[CENTRAL] Enviando a {len(cps_list)} CPs: {cps_list}")
                for id_cp in cps_list: # Para cada CP
                    orden = { # Creo la orden a enviar
                        "cp_id": id_cp, 
                        "cmd": cmd,
                        "timestamp": time.time()
                    }
                    # ENVIAR AL TOPIC ESPECÍFICO DEL CP
                    topic_destino = f"comandos_cp_{id_cp}"
                    payload = self._encrypt_for_cp(id_cp, orden)
                    self.productor.send(topic_destino, value=payload)
                    print(f"[CENTRAL] Comando {cmd} enviado a CP {id_cp} en topic {topic_destino}")
            else: # Si es para un CP específico
                if cp_id not in self.cps: # Si el CP no está registrado, envío mensaje
                    print(f"[CENTRAL] CP {cp_id} no encontrado. CPs registrados: {list(self.cps.keys())}")
                    return
                # si está registrado, envío el comando
                orden = { # creo la orden a enviar
                    "cp_id": cp_id, 
                    "cmd": cmd,
                    "timestamp": time.time()
                }
                # ENVIAR AL TOPIC ESPECÍFICO DEL CP
                topic_destino = f"comandos_cp_{cp_id}"
                payload = self._encrypt_for_cp(cp_id, orden)
                self.productor.send(topic_destino, value=payload)
                print(f"[CENTRAL] Comando {cmd} enviado a CP {cp_id} en topic {topic_destino}")
            self.productor.flush()
            print(f"[CENTRAL] Flush completado para comando {cmd}")
        except Exception as e: # Si ocurre un error
            print(f"[CENTRAL] ERROR al enviar comando: {e}")
            import traceback
            traceback.print_exc()

    def procesar_linea_monitor(self, linea: str, cliente=None): # Procesar comando recibido del monitor
        partes = (linea or "").strip().split() # Divido la línea en partes
        if len(partes) < 2: # Si no hay al menos 2 partes, es un comando inválido
            print(f"[CENTRAL] Comando inválido del monitor: {linea!r}")
            return

        comando, cp_id = partes[0].upper(), partes[1] # Obtengo el comando y el cp_id
        ahora = time.strftime("%H:%M:%S")
        
        with self._lock:
            self.cps.setdefault(cp_id, {"estado": EST_DESC}) # Aseguro que el CP esté registrado

            # Si NO es AUTH y no hay clave en memoria, exigir reauth ANTES de procesar comandos
            if comando != "AUTH":
                    clave = self.cps.get(cp_id, {}).get("clave_simetrica")
                    if not clave:
                        if cliente:
                            cliente.sendall(b"REAUTH_REQUIRED\n")
                        print(f"[CENTRAL] CP {cp_id} sin clave -> REAUTH_REQUIRED")
                        return 

            if comando == "AVISO": # Si recibo el comando "AVISO"
                print(f"[{ahora}] [CENTRAL] Monitor avisa de {cp_id}. Estado actual: {self.cps[cp_id]['estado']}")
            elif comando == "HELLO": # Si recibo el comando "HELLO"
                print(f"[{ahora}] [CENTRAL] Monitor avisa de {cp_id}. Estado actual: {self.cps[cp_id]['estado']} --> TODO OK")
            elif comando == "MON_AVERIA": # Si recibo el comando "MON_AVERIA"
                if self.cps[cp_id]["estado"] != EST_DESC: # Si el estado no es DESCONECTADO
                    self.cps[cp_id]["estado"] = EST_DESC # Actualizo el estado del cp a DESCONECTADO
                    print(f"[{ahora}] [CENTRAL] {cp_id} -> AVERIA (reportado por monitor)")
                    self.actualizar_estado_cp_en_bd(cp_id, EST_DESC) # Actualizo el estado en la BD
                    orden = {"cp_id": cp_id, "cmd": "DESCONECTADO"} # Creo la orden a enviar
                    payload = self._encrypt_for_cp(cp_id, orden)
                    self.productor.send(f"comandos_cp_{cp_id}", payload) # Envio la orden al topic del CP
                    self.productor.flush()
                    print(f"[CENTRAL] Comando DESCONECTADO enviado al CP {cp_id}")

            elif comando == "AUTH":
                # Formato esperado: AUTH <cp_id_bd> <credencial>
                if len(partes) < 3:
                    msg = "AUTH_ERROR faltan_parametros\n"
                    if cliente:
                        cliente.sendall(msg.encode())
                    print(f"[CENTRAL] AUTH inválido (faltan params): {linea!r}")
                    return

                credencial = partes[2]

                # 1) Validar en BD: cp existe, credencial coincide, activo=1
                ok = self.validar_cp_en_bd(cp_id, credencial)

                if ok:
                    # 2) Generar clave simétrica (por ahora la dejamos como texto hexadecimal)
                    clave = secrets.token_hex(16)  # 32 hex chars (=16 bytes)

                    # 3) Marcar que tiene clave (si tienes esa columna)
                    self.marcar_cp_con_clave(cp_id)

                    # 4) Guardar la clave en memoria (opcional pero útil)
                    self.cps.setdefault(cp_id, {})["clave_simetrica"] = clave

                    # 5) Responder al CP
                    msg = f"AUTH_OK {clave}\n"
                    if cliente:
                        cliente.sendall(msg.encode())
                    print(f"[{ahora}] [CENTRAL] AUTH OK para CP {cp_id}")
                else:
                    msg = "AUTH_ERROR credencial_invalida_o_inactivo\n"
                    if cliente:
                        cliente.sendall(msg.encode())
                    print(f"[{ahora}] [CENTRAL] AUTH ERROR para CP {cp_id}")

            elif comando == "EN_AVERIA": # Si recibo el comando "EN_AVERIA"
                if self.cps[cp_id]["estado"] != EST_DESC: # Si el estado no es DESCONECTADO
                    self.cps[cp_id]["estado"] = EST_AVERIA # Actualizo el estado del cp a AVERIA
                    print(f"[{ahora}] [CENTRAL] {cp_id} -> AVERIA (reportado por monitor)")
                    self.actualizar_estado_cp_en_bd(cp_id, EST_AVERIA) # Actualizo el estado en la BD
                    orden = {"cp_id": cp_id, "cmd": "AVERIA"} # Creo la orden a enviar
                    self.productor.send(f"comandos_cp_{cp_id}", orden) # Envio la orden al topic del CP
                    self.productor.flush()
                    print(f"[CENTRAL] Comando AVERIA enviado al CP {cp_id}")
            elif comando == "MON_RECUPERADO": # Si recibo el comando "MON_RECUPERADO"
                self.cps[cp_id]["estado"] = EST_ACTIVO # Actualizo el estado del cp a ACTIVADO
                print(f"[{ahora}] [CENTRAL] {cp_id} -> ACTIVADO (monitor recuperado)")
                self.actualizar_estado_cp_en_bd(cp_id, EST_ACTIVO) # Actualizo el estado en la BD
                orden = {"cp_id": cp_id, "cmd": "ACTIVADO"} # Creo la orden a enviar
                self.productor.send(f"comandos_cp_{cp_id}", orden) # Envio la orden al topic del CP
                self.productor.flush()
                print(f"[CENTRAL] Comando resolucion de contingenica enviado al CP {cp_id}")
            elif comando == "EN_RECUPERADO": # Si recibo el comando "EN_RECUPERADO"
                self.cps[cp_id]["estado"] = EST_ACTIVO # Actualizo el estado del cp a ACTIVADO
                print(f"[{ahora}] [CENTRAL] {cp_id} -> ACTIVADO (Engine recuperado)")
                self.actualizar_estado_cp_en_bd(cp_id, EST_ACTIVO) # Actualizo el estado en la BD
                orden = {"cp_id": cp_id, "cmd": "ACTIVADO"} # Creo la orden a enviar
                self.productor.send(f"comandos_cp_{cp_id}", orden) # Envio la orden al topic del CP
                self.productor.flush()
                print(f"[CENTRAL] Comando resolucion de contingenica enviado al CP {cp_id}")
            else: # Si no se reconcoce el comando
                print(f"[CENTRAL] Comando de monitor NO reconocido: {linea!r}")

            

    def atender_monitor(self, cliente, direccion): # Atender conexión de un monitor
        try: # Intento atender al monitor
            with cliente: # Conexión con el monitor
                acumulador = b"" # Acumulador de datos recibidos
                while True: # Bucle para recibir datos
                    datos = cliente.recv(1024) # Guardo los datos del monitor
                    if not datos: # Si no hay datos, salgo del bucle
                        break
                    acumulador += datos # Acumulo los datos recibidos
                    while b"\n" in acumulador: # Mientras haya líneas completas
                        linea_bytes, acumulador = acumulador.split(b"\n", 1) # Divido en línea y el resto
                        try: # Intento procesar la línea
                            linea = linea_bytes.decode(errors="ignore").strip() # Decodifico la línea
                            if not linea: # si la línea está vacía
                                continue
                            # sino esta vacía, proceso la línea
                            self.procesar_linea_monitor(linea,cliente) # Proceso la línea recibida
                            cliente.sendall(b"ACK\n") # Envio ACK al monitor
                        except Exception: # Si hay un error al procesar la línea
                            cliente.sendall(b"NACK\n") # Envio NACK al monitor
        except Exception as e: # Si hay un error con el monitor
            print(f"[CENTRAL] Error con monitor {direccion}: {e}")

    def servidor_monitores(self, host_escucha="0.0.0.0", puerto_escucha=7001): # Servidor para monitores
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor: # Creo el socket del servidor
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            servidor.bind((host_escucha, puerto_escucha)) # Enlazo el socket
            servidor.listen(10) # Escucho conexiones entrantes
            print(f"[CENTRAL] Escuchando monitores en {host_escucha}:{puerto_escucha}") # Mensaje de confirmación
            while True: # Bucle para aceptar conexiones
                conn, addr = servidor.accept() # Acepto la conexión
                threading.Thread( # Creo un hilo para atender al monitor
                    target=self.atender_monitor,
                    args=(conn, addr),
                    daemon=True
                ).start()

    def escuchar_alertas_meteorologicas(self): # Escuchar alertas meteorológicas desde EV_W
        consumidor = obtener_consumidor("alertas_meteorologicas", "central-alertas", self.servidor_kafka)
        print("[CENTRAL] Escuchando alertas meteorológicas...")

        for msg in consumidor:
            alerta = msg.value
            alert_type = alerta.get("alert_type")
            cp_id = alerta.get("cp_id")
            temperature = alerta.get("temperature")
            
            if not alert_type or not cp_id:
                continue
                
            print(f"[CENTRAL] Alerta meteorológica recibida para CP {cp_id}: {alert_type} ({temperature}°C)")
            
            # Determinar la acción según el tipo de alerta
            if alert_type == "bajo_zero":
                # Enviar comando de parada al CP específico
                self.enviar_comando_cp_por_alerta(cp_id, "PARAR", f"Parada por alerta meteorológica ({temperature}°C)")
                print(f"[CENTRAL] Enviando PARADA a CP {cp_id} por temperatura bajo cero")
            elif alert_type == "normal":
                # Enviar comando de reanudación si estaba parado por alerta
                with self._lock:
                    estado_actual = self.cps.get(cp_id, {}).get("estado", "")
                
                if estado_actual == "PARADO":
                    self.enviar_comando_cp_por_alerta(cp_id, "REANUDAR", f"Reanudación tras alerta meteorológica resuelta ({temperature}°C)")
                    print(f"[CENTRAL] Enviando REANUDACIÓN a CP {cp_id}")

    def enviar_comando_cp_por_alerta(self, cp_id, comando, motivo): # Enviar parada o reanudar a un CP por alerta o fin de alerta meteorologica
        try:
            orden = {
                "cp_id": cp_id,
                "cmd": comando,
                "motivo": motivo,
                "origen": "alerta_meteorologica",
                "timestamp": time.time()
            }
            
            # Enviar al topic específico del CP
            topic_destino = f"comandos_cp_{cp_id}"
            payload = self._encrypt_for_cp(cp_id, orden)
            self.productor.send(topic_destino, payload)

            self.productor.flush()
            print(f"[CENTRAL] Comando {comando} enviado a CP {cp_id} por alerta meteorológica")
            
            # Actualizar estado en memoria
            with self._lock:
                if cp_id in self.cps:
                    self.cps[cp_id]["estado"] = "PARADO" if comando == "PARAR" else "ACTIVADO"
            
        except Exception as e:
            print(f"[CENTRAL] ERROR al enviar comando por alerta: {e}")

    def actualizar_estado_driver(self, driver_id, nuevo_estado): # Acutaliza el estado de un conductor en BBDD
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "UPDATE conductor SET estado = %s WHERE id_conductor = %s"
            cursor.execute(consulta, (nuevo_estado, driver_id))
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"[CENTRAL] Estado de conductor {driver_id} actualizado a: {nuevo_estado}")
            return True
        except Exception as e:
            print(f"[CENTRAL] Error actualizando estado de conductor: {e}")
            conexion.close()
            return False

    def registrar_auditoria(self, ip_origen, accion, descripcion): # Registrar eventi en auditoria
        conexion = self.obtener_conexion_bd()
        if not conexion:
            return False
        
        try:
            cursor = conexion.cursor()
            consulta = "INSERT INTO auditoria (fecha_hora, ip_origen, accion, descripcion) VALUES (NOW(), %s, %s, %s)"
            cursor.execute(consulta, (ip_origen, accion, descripcion))
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"[AUDITORIA] Registrado: {accion} - {descripcion}")
            return True
        except Exception as e:
            print(f"[AUDITORIA] Error registrando auditoría: {e}")
            conexion.close()
            return False

    def escuchar_cambios_estado_driver(self): # Escuchar cambios de estado de drivers
        consumidor = obtener_consumidor(TOPIC_CAMBIOS_ESTADO_DRIVER, 'central-estados-driver', self.servidor_kafka)
        print("[CENTRAL] Escuchando cambios de estado de drivers...")
        
        for msg in consumidor:
            cambio = msg.value
            driver_id = cambio.get('driver_id')
            nuevo_estado = cambio.get('nuevo_estado')
            cp_id = cambio.get('cp_id')
            
            if not driver_id or not nuevo_estado:
                continue
            
            print(f"[CENTRAL] Recibido cambio de estado para driver {driver_id}: {nuevo_estado}")
            
            # Actualizar estado en BD
            if self.actualizar_estado_driver(driver_id, nuevo_estado):
                print(f"[CENTRAL] Estado del driver {driver_id} actualizado a: {nuevo_estado}")
                
                # Registrar en auditoría si es suministro
                if "Suministrando" in nuevo_estado:
                    self.registrar_auditoria(f"CP-{cp_id}", "inicio_suministro",
                                            f"Driver {driver_id} iniciando suministro en CP {cp_id}")
    def revocar_clave_cp(self, cp_id: str):
        # 1) BD: marcar que ya no tiene clave
        conexion = self.obtener_conexion_bd()
        if conexion:
            try:
                cur = conexion.cursor()
                cur.execute("""
                    UPDATE punto_recarga
                    SET tiene_clave_simetrica = 0
                    WHERE id_punto_recarga = %s
                """, (cp_id,))
                conexion.commit()
                cur.close()
                conexion.close()
            except Exception as e:
                print(f"[CENTRAL] Error revocando clave en BD para CP {cp_id}: {e}")
                try: conexion.close()
                except: pass

        # 2) Memoria: borrar clave
        with self._lock:
            if cp_id in self.cps and "clave_simetrica" in self.cps[cp_id]:
                del self.cps[cp_id]["clave_simetrica"]

        print(f"[CENTRAL] Clave simétrica revocada para CP {cp_id}.")

    def iniciar_servicios(self): # Iniciar todos los servicios de la central
        print("Iniciando todos los servicios de la central...")
        
        # Crear hilos para cada tipo de mensaje
        hilo_verificaciones = threading.Thread(target=self.escuchar_peticiones_verificacion, daemon=True) # Hilo para verificación de conductores
        hilo_cargas = threading.Thread(target=self.escuchar_peticiones_recarga, daemon=True) # Hilo para peticiones de recarga
        hilo_registros = threading.Thread(target=self.escuchar_registros_cp, daemon=True) # Hilo para registros de CPs
        hilo_estados = threading.Thread(target=self.escuchar_estados_cp, daemon=True) # Hilo para estados de CPs
        hilo_monitores = threading.Thread(target=self.servidor_monitores, daemon=True) # Hilo para atender monitores
        hilo_consultas = threading.Thread(target=self.escuchar_consultas_cps, daemon=True) # Hilo para consultas de CPs disponibles
        hilo_alertas = threading.Thread(target=self.escuchar_alertas_meteorologicas, daemon=True)
        hilo_estados_driver = threading.Thread(target=self.escuchar_cambios_estado_driver, daemon=True)
        
        # Iniciar todos los hilos
        hilo_verificaciones.start()
        hilo_cargas.start()
        hilo_registros.start()
        hilo_estados.start()
        hilo_monitores.start()
        hilo_consultas.start()
        hilo_alertas.start()
        hilo_estados_driver.start()

        print("Todos los servicios iniciados. La central está operativa.") # Confirmación

    def mostrar_menu_central(self): # Mostrar el menú de la central en terminal
        try: # Intento mostrar el menú
            while self.activo: # Mientras la central esté activa
                # Imprimo la información del menú
                print("\n" + "="*60)
                print("          MENÚ DE CONTROL DE LA CENTRAL")
                print("="*60)
                print("1. Parar un CP específico")
                print("2. Parar todos los CPs")
                print("3. Reanudar un CP específico")
                print("4. Reanudar todos los CPs")
                print("5. Revocar clave simétrica de un CP")
                print("6. Salir")
                print("="*60)

                opcion = input("Seleccione una opción (1-5): ").strip() # Solicito la opción

                if opcion == '1': # Parar un CP específico
                    cp_id = input("Ingrese el ID del CP a PARAR: ").strip()
                    if cp_id in self.cps:  # Verificar que existe
                        self.enviar_comando(cp_id, "PARAR") # Enviar comando PARAR al CP específico
                    else: # Si no existe
                        print(f"CP {cp_id} no encontrado en central")
                elif opcion == '2': # Parar todos los CPs
                    if self.cps:  # Verificar que hay CPs
                        self.enviar_comando("ALL", "PARAR") # Enviar comando PARAR a todos
                    else: # Si no hay CPs
                        print("No hay CPs registrados en la central")
                elif opcion == '3': # Reanudar un CP específico
                    cp_id = input("Ingrese el ID del CP a REANUDAR: ").strip() # Solicito el ID del CP
                    if cp_id in self.cps:  # Verificar que existe
                        self.enviar_comando(cp_id, "REANUDAR") # Enviar comando REANUDAR al CP específico
                    else: # Si no existe
                        print(f"CP {cp_id} no encontrado en central")
                elif opcion == '4': # Reanudar todos los CPs
                    if self.cps:  # Verificar que hay CPs
                        self.enviar_comando("ALL", "REANUDAR") # Enviar comando REANUDAR a todos
                    else: # Si no hay CPs
                        print("No hay CPs registrados en la central")
                elif opcion == '5': # Revocar clave simétrica de un CPelif opcion == '5':
                    cp_id = input("Ingrese el ID del CP para REVOCAR CLAVE: ").strip()
                    self.revocar_clave_cp(cp_id)
                elif opcion == '6': # Salir del menú
                    print("Saliendo del menú de la central...")
                    self.activo = False  # detener monitoreo
                    break
                else: # Opción no válida
                    print("Opción no válida. Intente de nuevo.")

        except KeyboardInterrupt: # Si hago Ctrl + C
            print("\nSaliendo del menú por interrupción...")
        except Exception as e: # Si ocurre otro error
            print(f"Error en el menú de la central: {e}")

    def ver_cps_bd(self): # Obtener información de todos los CPS en la BD
        conexion = self.obtener_conexion_bd() # Nueva conexión a BD
        if not conexion: # Si no hay conexión
            return {"total_cps": 0, "cps": []} # devuelvo una tupla vacía
        
        try: # Si hay conexión, intento obtener la información
            cursor = conexion.cursor()
            consulta = "SELECT id_punto_recarga, estado FROM punto_recarga ORDER BY id_punto_recarga"
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            # Procesar resultados
            cps_info = [ # Creo una lista de diccionarios con la información de los CPs
                {"id": cp[0], "estado": cp[1]}
                for cp in resultados
            ]
            
            info_completa = { # Creo el diccionario con la información completa
                "total_cps": len(resultados),
                "cps": cps_info
            }
            
            # Usar los mismos colores definidos en iniciar_monitoreo_estados
            COLOR_RESET = "\033[0m"
            COLOR_VERDE = "\033[92m"
            COLOR_NARANJA = "\033[93m"
            COLOR_ROJO = "\033[91m"
            COLOR_GRIS = "\033[90m"
            
            print(f"[BD] Encontrados {info_completa['total_cps']} CPs en la base de datos") # Confirmación
            
            # Imprimir cada CP con su color correspondiente
            for cp in cps_info: # Para cada CP
                estado = cp["estado"] # Obtengo el estado
                color = COLOR_RESET  # Por defecto
                
                # Asignar color según el estado (igual que en iniciar_monitoreo_estados)
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
                
                print(f"ID: {cp['id']}, ESTADO: {color}\"{estado}\"{COLOR_RESET}") # Imprimo el CP con color
                
            return info_completa
        except Exception as e: # Si ocurre un error
            print(f"Error al obtener información de CPs en BD: {e}")
            conexion.close()
            return {"total_cps": 0, "cps": []} # devuelvo una tupla vacía

    def iniciar_monitoreo_estados(self): # Iniciar monitoreo de estados de CPs y mostrarlos en terminal
        def mostrar_estados_periodicamente(): # Función interna para mostrar estados periódicamente
            # Definir colores para estados
            COLOR_RESET = "\033[0m"
            COLOR_VERDE = "\033[92m"
            COLOR_NARANJA = "\033[93m"
            COLOR_ROJO = "\033[91m"
            COLOR_GRIS = "\033[90m"

            while self.activo: # Mientras la central esté activa
                # Imprimir información
                print("\n" + "="*50)
                print("          ESTADOS ACTUALES DE CPs")
                print("="*50)
                
                # Llamar a la función que muestra CPs de BD con colores
                self.ver_cps_bd()
                time.sleep(2)
                print("-" * 50)
                print("          ESTADOS EN MEMORIA DE LA CENTRAL")
                print("-" * 50)

                if not self.cps: # Si no hay CPs conectados
                    print("No hay CPs conectados con la central")
                else: # Si hay CPs conectados
                    for cp_id, datos in self.cps.items(): # Para cada CP en memoria
                        estado = datos.get("estado", "N/A") # Obtengo el estado
                        ubicacion = datos.get("ubicacion", "N/A") # Obtengo la ubicación
                        color = COLOR_RESET # Color por defecto

                        # Asigno color según el estado
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

                        print(f"{color}{cp_id}: {estado} - {ubicacion}{COLOR_RESET}") # Imprimo el estado con color
                
                print("="*50)
                time.sleep(10) # Esperar antes de la siguiente actualización

        threading.Thread(target=mostrar_estados_periodicamente, daemon=True).start() # Iniciar hilo para mostrar estados periódicamente

def main(): # Función main
    if len(sys.argv) < 3: # Si los argumentos son incorrectos
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Central.py <IP:puerto_broker> <IP:puerto_BD>")
        sys.exit(1) # Devuelvo error y salgo
    
    servidor_kafka = sys.argv[1] # Servidor Kafka
    servidor_bd = sys.argv[2] # Servidor BD

    print(f"Kafka: {servidor_kafka}. BD: {servidor_bd}") # Confirmación

    ev_central = EV_Central(servidor_kafka, servidor_bd) # Creo e inicializo la central

    # PRIMERO iniciar el monitoreo de estados
    ev_central.iniciar_monitoreo_estados()
    time.sleep(3) # Esperar un momento para que el monitoreo inicie

    def notificar_desconexion_central(): # Notificar a todos los CPs y drivers sobre la desconexión de la central
        print("\n[CENTRAL] Notificando desconexión a todos los componentes...")
        
        # Cambiar estado de todos los conductores a "Desconectado"
        conexion = ev_central.obtener_conexion_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("UPDATE conductor SET estado = 'Desconectado'")
                conexion.commit()
                cursor.close()
                conexion.close()
                print("[CENTRAL] Todos los conductores marcados como Desconectados")
            except Exception as e:
                print(f"[CENTRAL] Error actualizando estados de conductores: {e}")

        # Notificar a todos los CPs registrados
        for cp_id in ev_central.cps.keys(): # Para cada CP registrado
            mensaje_desconexion = { # Creo el mensaje de desconexión
                "tipo": "DESCONEXION_CENTRAL",
                "cp_id": cp_id,
                "timestamp": time.time(),
                "mensaje": "La central se está desconectando. Espere a que vuelva a estar operativa."
            }
            try: # Intento enviar el mensaje
                ev_central.productor.send(f"comandos_cp_{cp_id}", mensaje_desconexion) # Envio el mensaje al topic del CP
                print(f"[CENTRAL] Notificación enviada a CP {cp_id}")
            except Exception as e: # Si ocurre un error
                print(f"[CENTRAL] Error al notificar a CP {cp_id}: {e}")
        
        # Notificar a todos los drivers (topic general)
        mensaje_driver = { # Creo el mensaje de desconexión para drivers
            "tipo": "DESCONEXION_CENTRAL",
            "timestamp": time.time(),
            "mensaje": "La central se está desconectando. Espere a que vuelva a estar operativa."
        }
        try: # Intento enviar el mensaje
            ev_central.productor.send('respuestas_conductor', mensaje_driver) # Envio el mensaje al topic de drivers
            ev_central.productor.send('respuestas_consultas_cps', mensaje_driver) # Envio el mensaje al topic de consultas de CPs
            print("[CENTRAL] Notificación enviada a drivers")
        except Exception as e: # Si ocurre un error
            print(f"[CENTRAL] Error al notificar a drivers: {e}")
        
        # Esperar a que los mensajes se envíen
        try:
            ev_central.productor.flush(timeout=2.0)
            print("[CENTRAL] Todos los mensajes de desconexión enviados")
        except Exception as e:
            print(f"[CENTRAL] Error al hacer flush: {e}")

    hilo_servicios = threading.Thread(target=ev_central.iniciar_servicios, daemon=True) # Hilo para iniciar servicios
    hilo_servicios.start() # Iniciar hilo de servicios

    # Esperar un momento para que los servicios se inicien completamente
    time.sleep(2)

    # LUEGO iniciar el menú (en el hilo principal)
    try: # Intento mostrar el menú
        ev_central.mostrar_menu_central() # Mostrar el menú de la central
        
        # Cuando el menú termine, notificar desconexión
        notificar_desconexion_central() # Notificar desconexión a todos los componentes
        print("\nCerrando central...")
        ev_central.activo = False
        
        # Dar tiempo para que los servicios se cierren correctamente
        time.sleep(2)
        
        print("Central cerrada correctamente")
    except KeyboardInterrupt: # Si hago Ctrl + C
        print("\nInterrupción recibida. Cerrando central...")
        
        # Notificar desconexión antes de cerrar
        notificar_desconexion_central() # Notificar desconexión a todos los componentes
        
        ev_central.activo = False
        time.sleep(2) # Dar tiempo para que los servicios se cierren correctamente
        print("Central cerrada correctamente") # Confirmación
    
    # SALIR DEL PROGRAMA
    sys.exit(0)

if __name__ == "__main__": # Llamada a Main
    main()