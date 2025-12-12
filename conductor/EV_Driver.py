import sys
import json
from kafka import KafkaProducer, KafkaConsumer
import time
import json
import threading
import os

# TOPICS
RESPUESTAS_CONDUCTOR = 'respuestas_conductor'
RESPUESTAS_CONSULTAS_CPS = 'respuestas_consultas_cps'
TOPIC_CONDUCTOR = 'conductor'
TOPIC_CONSULTAS_CPS = 'consultas_cps'
TOPIC_CARGA_SOLICITADA = 'CARGA_SOLICITADA'

def obtener_productor(servidor_kafka): # Obtener el productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )

def obtener_consumidor(grupo_id, servidor_kafka): # Obtener el consumidor de Kafka
    topics = [RESPUESTAS_CONDUCTOR, RESPUESTAS_CONSULTAS_CPS] # Topics para el consumidor
    return KafkaConsumer(
        *topics, # * Para desempaquetar la lista
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id=grupo_id,
        auto_offset_reset='latest',
    )

class EvDriver: # Clase conductor
    def __init__(self, driver_id, servidor_kafka, archivo=None): # Inicializamos las variables nedesarias
        self.driver_id = driver_id
        self.productor = obtener_productor(servidor_kafka)
        self.verificado = False # Verificación del conductor
        self.servidor_kafka = servidor_kafka
        self.respuestas_pendientes = 0 # Respuestas pendientes de la central por confirmar al Driver
        self.finalizar = False # Finalizar hilo
        self.hilo_activo = True # Hilo activo
        self.respuesta_recibida = False # Respuesta recibida de la central

        self.lista_cargas = [] # Lista de recargas desde archivo
        self.recarga_actual = 0 # Índice de recarga actual
        self.modo_manual = False # Activación del modo manual o automático (fichero)
        self.recarga_activa = False # Indica si hay una recarga activa
        self.cp_actual = None
        self.consulta_cps_pendiente = False
        self.cps_disponibles = [] # Lista de CPs disponibles para mostrar

        if archivo:
            self.cargar_recargas(archivo) # Si se ejecuta con archivo, cargamos las recargas
        else:
            self.modo_manual = True

        print("Inicializando conductor...")
        
        self.escuchar_respuestas() # Primero activamos hilo para escuchar a la central
        self.verificar_driver() # Verificamos el driver

        tiempo_espera = time.time() # Esperamos respuesta de verificación
        while not self.respuesta_recibida and (time.time() - tiempo_espera < 30): # Timeout de 30 segundos
            time.sleep(0.5)

        if self.verificado: # Si el driver está verificado, continuamos
            print(f"Conductor {driver_id} inicializado y conectado a Kafka: {servidor_kafka}")
            
            if self.modo_manual: # Si está en modo manual, mostramos el menú
                self.mostrar_menu()
            else:
                self.procesar_siguiente_recarga()
        else: # Si no está verificado, salimos
            print("ERROR: Conductor no verificado. Saliendo...")
            self.finalizar = True
    
    def cargar_recargas(self, archivo): # Cargar recargas desde archivo
        try:
            ruta_carpeta = 'recargas'
            ruta_completa = os.path.join(ruta_carpeta, archivo) # Cogemos la ruta completa

            if os.path.exists(ruta_completa): # Si la ruta es correcta y el archivo existe, lo leemos
                with open(ruta_completa, 'r', encoding='utf-8') as extraer:
                    for linea_num, linea in enumerate(extraer, 1):
                        cp_id = linea.strip()
                        self.lista_cargas.append(cp_id) # Añadimos el CP a la lista
            else: # De lo contrario
                self.modo_manual = True # Activamos modo manual
        except Exception as e:
            print(f"ERROR al cargar archivo: {e}")

    def procesar_siguiente_recarga(self): # Procesar la siguiente recarga en caso de que esté el modo automático
        if self.recarga_actual < len(self.lista_cargas):
            cp_id = self.lista_cargas[self.recarga_actual]
            print(f"Procesando recarga {self.recarga_actual + 1}/{len(self.lista_cargas)}: CP {cp_id}")
            self.solicitar_recarga(cp_id) # Solicitamos la recarga
        else: # Si ya no hay más recargas
            print("Todas las recargas procesadas")
            self.finalizar = True

    def verificar_driver(self): # Verificamos si el Driver está registrado en la BD
        mensaje = { # Construimos el mensaje
            'type': 'VERIFICAR_DRIVER',
            'driver_id': self.driver_id,
            'timestamp': time.time()
        }
        
        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            self.productor.send(TOPIC_CONDUCTOR, mensaje) # Enviamos el mensaje a central
            self.productor.flush()
            print(f"Verificando si el conductor {self.driver_id} está registrado en la Base de Datos...")
            return True
        except Exception as e:
            self.respuestas_pendientes -= 1
            print(f"ERROR al verificar al Conductor: {e}")
            return False

    def escuchar_respuestas(self): # Hilo para escuchar respuestas de la central
        def escuchar():
            consumidor = obtener_consumidor(f"driver-{self.driver_id}-{int(time.time())}", self.servidor_kafka) # Grupo para escuchar el driver con un cp_id específico

            for msg in consumidor: # Bucle para escuchar mensajes
                if not self.hilo_activo: # Si el hilo no está activo, salimos
                    break

                respuesta = msg.value # Guardamos el valor del mensaje

                if respuesta.get('tipo') == 'DESCONEXION_CENTRAL': # Si obtenemos una desconexion de la central
                    mensaje = respuesta.get('mensaje', 'La central se ha desconectado')
                    print(f"\n[EV_Driver]: {mensaje}")
                    print("Esperando a que la central vuelva a estar operativa...")
                    continue
                if respuesta.get('tipo') == 'CENTRAL_OPERATIVA': # Si obtenemos una reactivación de la central
                    mensaje = respuesta.get('mensaje', 'La central está operativa nuevamente')
                    print(f"\n[EV_Driver]: {mensaje}")
                    print("Puede continuar ejecutando comandos")
                    # Re-verificar el driver si es necesario
                    if not self.verificado: # Si no está verificado
                        print("Re-verificando conductor con la central...")
                        self.verificar_driver() # Verificamos
                    continue
                if respuesta.get('driver_id') == self.driver_id: # Si el mensaje es para este driver
                    self.respuestas_pendientes -= 1
                    self.respuesta_recibida = True

                    if 'exists' in respuesta: # Si contiene 'exists' (respuesta de verificacin)
                        if respuesta['exists'] is True: # Si el driver está registrado
                            self.verificado = True
                            print(f"Conductor verificado correctamente. Puede solicitar recargas.")
                        else: # Si no está registrado
                            print(f"ERROR: Conductor no registrado en la Base de Datos.")
                            print("Contacte con un administrador para darse de alta.")
                            self.finalizar = True
                    elif 'confirmacion' in respuesta: # Si contiene 'confirmación' (respuesta a solicitud de recarga)
                        cp_id = respuesta.get('cp_id')
                        if respuesta['confirmacion'] is True: # Si confirma la recarga
                            self.recarga_activa = True
                            self.cp_actual = cp_id
                            print(f"Recarga confirmada en CP: {cp_id}")
                            print("Iniciando proceso de recarga...")

                            # Si no está en modo manual, esperamos 4 segundos y procesamos la siguiente recarga)
                            # En modo manual no hace falta porque ya se tarda más de 4 segundos en procesar la siguiente recarga
                            if not self.modo_manual:
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()
                        else: # Si rechaza la recarga
                            print(f"ERROR: Recarga de {self.driver_id} RECHAZADA en CP: {cp_id}")
                            
                            if not self.modo_manual: # Esperamos 4 segundos
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()
                    elif respuesta.get('type') == 'RESPUESTA_CPS_DISPONIBLES' and respuesta.get('driver_id') == self.driver_id: # Si es respuesta a la consulta de CPs disponibles
                        self.cps_disponibles = respuesta.get('cps_disponibles', []) # Los obtenemos
                        self.consulta_cps_pendiente = False
                        print(f"Recibida información de {len(self.cps_disponibles)} CPs disponibles")
                    elif 'estado_carga' in respuesta and respuesta['estado_carga'] == 'recarga_finalizada': # Si la recarga ha finalizado, imprimimos el ticket
                        energia = respuesta.get('energia_kwh', 0)
                        importe = respuesta.get('importe_eur', 0)
                        mensaje = respuesta.get('mensaje', '')
                        print(f"\n\nTICKET FINAL: {mensaje}")
                        print(f"   Energía consumida: {energia:.2f} kWh")
                        print(f"   Importe total: {importe:.2f} €")
                        
                        self.recarga_activa = False
                        self.cp_actual = None

            if not self.hilo_activo: # Si el hilo no está activo, salimos
                self.finalizar = True

        hilo_escucha = threading.Thread(target=escuchar, daemon=True)
        hilo_escucha.start()
    
    def consultar_cps_disponibles(self): # Consultar con central los CPs disponibles
        consulta_id = f"{self.driver_id}_{int(time.time())}"
        
        mensaje = { # Construimos el mensaje a enviar a la central
            'type': 'CONSULTA_CPS_DISPONIBLES',
            'driver_id': self.driver_id,
            'consulta_id': consulta_id,
            'timestamp': time.time()
        }
        
        try:
            self.consulta_cps_pendiente = True
            self.cps_disponibles = []  # Resetear lista
            self.productor.send(TOPIC_CONSULTAS_CPS, mensaje) # Enviamos el mensaje a central con un topic específico
            self.productor.flush()
            print("Consultando CPs disponibles...")
            
            tiempo_espera = time.time() # Esperar respuesta
            while self.consulta_cps_pendiente and (time.time() - tiempo_espera < 10):  # Timeout 10 segundos
                time.sleep(0.5)
            
            if self.consulta_cps_pendiente: # Si se sobrepasa el tiempo de espera
                print("ERROR Timeout: No se recibieron CPs disponibles")
                self.consulta_cps_pendiente = False
                return False
            return True # De lo contrario
        except Exception as e:
            print(f"ERROR al consultar CPs disponibles: {e}")
            self.consulta_cps_pendiente = False
            return False

    def mostrar_cp_disponibles(self): # Mostrar los CPs disponibles
        # Imprimimos los CPs disponibles, con una pequeña interfaz en terminal
        print("\n" + "="*60)
        print("          PUNTOS DE CARGA DISPONIBLES")
        print("="*60)
        
        if not self.consultar_cps_disponibles(): # Si no se pudieron consultar, salimos
            return
        
        if not self.cps_disponibles: # Si no hay, lo indicamos y salimos de la opción
            print("No hay puntos de carga disponibles en este momento")
            print("Los CPs pueden estar: PARADOS, EN AVERÍA, DESCONECTADOS o SUMINISTRANDO")
            return
        
        # Imprimimos la información obtenida
        print(f"Se encontraron {len(self.cps_disponibles)} punto(s) de carga disponible(s):\n")
        print(f"{'ID CP':<15} {'UBICACIÓN':<25} {'PRECIO (€/kWh)':<15}")
        print("-" * 60)
        
        for cp in self.cps_disponibles:
            print(f"{cp['cp_id']:<15} {cp['ubicacion']:<25} {cp['precio']:<15.3f}")
        
        print("=" * 60)


    def mostrar_menu(self): # Menú del condctor
        while not self.finalizar: # Bucle para que no se cierre el menú
            # Imprimimos la información
            print("\n" + "="*50)
            print("          MENÚ EV_DRIVER")
            print("="*50)
            print("1. Solicitar recarga")
            print("2. Ver estado actual")
            print("3. Mostrar CP disponibles para suministrar")
            print("4. Salir")
            print("="*50)
            
            try:
                opcion = input("Seleccione una opción (1-4): ").strip() # Seleccionamos la opción
                
                if opcion == '1': # Si solicitamos recarga
                    if self.recarga_activa: # Si hay una activa ya
                        print("Ya hay una recarga activa. Finalice la actual primero.")
                    else: # De lo contrario
                        cp_id = input("Ingrese el ID del punto de carga: ").strip() # Ingramso el ID del CP
                        if cp_id: # Si nos introducen el cp_id
                            print("Esperando confirmación del punto de carga...")
                            self.solicitar_recarga(cp_id) # Solicitamos la recarga
                        else: # Si no, devolvemos error
                            print("Debe ingresar un ID de un punto de carga válido")
                elif opcion == '2': # Mostramos el estado actual del driver
                    self.mostrar_estado()
                elif opcion == '3': # Mostramos los CP disponibles para suministrar
                    print("Mostrando todos los CP diponibles para suministrar...")
                    self.mostrar_cp_disponibles()
                elif opcion == '4': # Salir
                    print("Saliendo del sistema...")
                    self.finalizar = True
                    break
                else:
                    print("Opción no válida. Intentelo de nuevo.")
            
            except KeyboardInterrupt: # Si pulsamos Ctrl + C
                print("\naliendo del sistema ...")
                self.finalizar = True
                break
            except Exception as e:
                print(f"ERROR: {e}")

    def mostrar_estado(self): # Impresión del estado del driver
        print("\n--- ESTADO ACTUAL ---")
        print(f"Conductor: {self.driver_id}")
        print(f"Verificado: {'Sí' if self.verificado else 'No'}")
        print(f"Recarga activa: {'Sí' if self.recarga_activa else 'No'}")
        if self.recarga_activa:
            print(f"CP actual: {self.cp_actual}")
        print(f"Respuestas pendientes: {self.respuestas_pendientes}")
        print("-------------------")

    def finalizar_recarga(self): # Para indicar que se finaliza la recarga tras finalizarla en el CP
        if self.recarga_activa: # Si hay recarga activa
            print(f"Finalizando recarga en CP: {self.cp_actual}...") # Finalizamos y reseteamos los parámetros
            self.recarga_activa = False
            self.cp_actual = None
            print("Recarga finalizada correctamente")
        else: # Si no hay
            print("No hay recarga activa para finalizar")

    def solicitar_recarga(self, cp_id):
        if not self.verificado:
            print("Conductor no verificado. No puede solicitar recargas")
            return False
        
        print(f"\n[DRIVER] Cambiando estado a: Esperando Confirmacion Central")
        
        mensaje = {
            'driver_id': self.driver_id,
            'cp_id': cp_id,
            'type': 'SOLICITAR_RECARGA',
            'timestamp': time.time()
        }

        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            self.productor.send(TOPIC_CARGA_SOLICITADA, mensaje)
            self.productor.flush()
            print(f"Solicitud de recarga enviada del Conductor {self.driver_id} al Punto de Carga {cp_id}")
            
            # Esperamos a que el servidor responda
            tiempo_espera = time.time()
            while not self.respuesta_recibida and (time.time() - tiempo_espera < 30):
                time.sleep(0.5)
            
            if not self.respuesta_recibida:
                print("ERROR Timeout: No se recibió respuesta del servidor")
                self.respuestas_pendientes -= 1
            
            return True
        except Exception as e:
            self.respuestas_pendientes -= 1
            print(f"ERROR al solicitar recarga: {e}")
            return False
    
    def detener_escucha(self): # Detener el hilo de escucha
        self.hilo_activo = False
        self.finalizar = True

def main(): # Función Main
    if len(sys.argv) < 3: # Si no están los argumentos correctos
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Driver.py <IP:puerto_broker> <id_driver> [nombre_archivo_recargas]")
        sys.exit(1) # Error y salimos
    
    servidor_kafka = sys.argv[1] # Servidor de kafka
    id_driver = sys.argv[2] # id del driver
    archivo = sys.argv[3] if len(sys.argv) > 3 else None # archivo de recargas, en caso de que haya

    ev_driver = EvDriver(id_driver, servidor_kafka, archivo) # Inicializamos el conductor
    
    if not ev_driver.modo_manual: # Si no está en modo manual, esperamos a que termine todas las recargas
        tiempo_inicio = time.time()
        while (ev_driver.respuestas_pendientes != 0 or not ev_driver.finalizar) and (time.time() - tiempo_inicio < 90):
            time.sleep(1)

    ev_driver.detener_escucha() # Detenemos el hilo de escucha
    print("\nApagando conductor...")
    print('FIN: EV_Driver.py')

if __name__ == "__main__": # Llamada al main
    main()