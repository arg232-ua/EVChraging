import sys
import json
from kafka import KafkaProducer, KafkaConsumer
import time
import json
import threading
import os

def obtener_productor(servidor_kafka):
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )

def obtener_consumidor(grupo_id, servidor_kafka):
    topics = ['respuestas_conductor','respuestas_consultas_cps']
    return KafkaConsumer(
        *topics, # * Para desempaquetar la lista
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id=grupo_id,
        auto_offset_reset='latest',
    )

class EvDriver:
    def __init__(self, driver_id, servidor_kafka, archivo=None):
        self.driver_id = driver_id
        self.productor = obtener_productor(servidor_kafka)
        self.verificado = False
        self.servidor_kafka = servidor_kafka
        self.respuestas_pendientes = 0
        self.finalizar = False
        self.hilo_activo = True
        self.respuesta_recibida = False

        self.lista_cargas = []
        self.recarga_actual = 0
        self.modo_manual = False
        self.recarga_activa = False
        self.cp_actual = None
        self.consulta_cps_pendiente = False
        self.cps_disponibles = []

        if archivo:
            self.cargar_recargas(archivo)
        else:
            self.modo_manual = True

        print("Inicializando conductor...")
        
        self.escuchar_respuestas()
        self.verificar_driver()

        tiempo_espera = time.time()
        while not self.respuesta_recibida and (time.time() - tiempo_espera < 30):
            time.sleep(0.5)

        if self.verificado:
            print(f"Conductor {driver_id} inicializado y conectado a Kafka: {servidor_kafka}")
            
            if self.modo_manual:
                self.mostrar_menu()
            else:
                self.procesar_siguiente_recarga()
        else:
            print("Error: Conductor no verificado. Saliendo...")
            self.finalizar = True
    
    def cargar_recargas(self, archivo):
        try:
            ruta_carpeta = 'recargas'
            ruta_completa = os.path.join(ruta_carpeta, archivo)

            if os.path.exists(ruta_completa):
                with open(ruta_completa, 'r', encoding='utf-8') as extraer:
                    for linea_num, linea in enumerate(extraer, 1):
                        cp_id = linea.strip()
                        self.lista_cargas.append(cp_id)
            else:
                self.modo_manual = True
        except Exception as e:
            print(f"Error al cargar archivo: {e}")

    def procesar_siguiente_recarga(self):
        if self.recarga_actual < len(self.lista_cargas):
            cp_id = self.lista_cargas[self.recarga_actual]
            print(f"Procesando recarga {self.recarga_actual + 1}/{len(self.lista_cargas)}: CP {cp_id}")
            self.solicitar_recarga(cp_id)
        else:
            print("Todas las recargas procesadas")
            self.finalizar = True

    def verificar_driver(self):
        mensaje = {
            'type': 'VERIFICAR_DRIVER',
            'driver_id': self.driver_id,
            'timestamp': time.time()
        }
        
        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            self.productor.send('conductor', mensaje)
            self.productor.flush()
            print(f"Verificando si el conductor {self.driver_id} está registrado en la Base de Datos...")
            return True
        except Exception as e:
            self.respuestas_pendientes -= 1
            print(f"Error al verificar al Conductor: {e}")
            return False

    def escuchar_respuestas(self):
        def escuchar():
            consumidor = obtener_consumidor(f"driver-{self.driver_id}-{int(time.time())}", self.servidor_kafka)

            for msg in consumidor:
                if not self.hilo_activo:
                    break

                respuesta = msg.value

                if respuesta.get('driver_id') == self.driver_id:
                    self.respuestas_pendientes -= 1
                    self.respuesta_recibida = True

                    if 'exists' in respuesta:
                        if respuesta['exists'] is True:
                            self.verificado = True
                            print(f"✅ Conductor verificado correctamente. Puede solicitar recargas.")
                        else:
                            print(f"❌ Conductor no registrado en la Base de Datos.")
                            print("Contacte con un administrador para darse de alta.")
                            self.finalizar = True
                    
                    elif 'confirmacion' in respuesta:
                        cp_id = respuesta.get('cp_id')
                        if respuesta['confirmacion'] is True:
                            self.recarga_activa = True
                            self.cp_actual = cp_id
                            print(f"✅ Recarga confirmada en CP: {cp_id}")
                            print("Recarga en progreso...")
                            
                            # Falta logica de CPS ######################################

                            if not self.modo_manual:
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()
                        else:
                            print(f"❌ Recarga de {self.driver_id} RECHAZADA en CP: {cp_id}")
                            
                            if not self.modo_manual:
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()
                    elif respuesta.get('type') == 'RESPUESTA_CPS_DISPONIBLES' and respuesta.get('driver_id') == self.driver_id:
                        self.cps_disponibles = respuesta.get('cps_disponibles', [])
                        self.consulta_cps_pendiente = False
                        print(f"✅ Recibida información de {len(self.cps_disponibles)} CPs disponibles")
                    elif 'estado_carga' in respuesta and respuesta['estado_carga'] == 'recarga_finalizada':
                        energia = respuesta.get('energia_kwh', 0)
                        importe = respuesta.get('importe_eur', 0)
                        mensaje = respuesta.get('mensaje', '')
                        print(f"\n\n🎫 TICKET FINAL: {mensaje}")
                        print(f"   Energía consumida: {energia:.2f} kWh")
                        print(f"   Importe total: {importe:.2f} €")
                        
                        self.recarga_activa = False
                        self.cp_actual = None

            if not self.hilo_activo:
                self.finalizar = True

        hilo_escucha = threading.Thread(target=escuchar, daemon=True)
        hilo_escucha.start()
    
    def consultar_cps_disponibles(self): # Consultar con central los CPs disponibles
        consulta_id = f"{self.driver_id}_{int(time.time())}"
        
        mensaje = {
            'type': 'CONSULTA_CPS_DISPONIBLES',
            'driver_id': self.driver_id,
            'consulta_id': consulta_id,
            'timestamp': time.time()
        }
        
        try:
            self.consulta_cps_pendiente = True
            self.cps_disponibles = []  # Resetear lista
            self.productor.send('consultas_cps', mensaje)
            self.productor.flush()
            print("Consultando CPs disponibles...")
            
            # Esperar respuesta
            tiempo_espera = time.time()
            while self.consulta_cps_pendiente and (time.time() - tiempo_espera < 10):  # Timeout 10 segundos
                time.sleep(0.5)
            
            if self.consulta_cps_pendiente:
                print("❌ Timeout: No se recibieron CPs disponibles")
                self.consulta_cps_pendiente = False
                return False
            return True
        except Exception as e:
            print(f"❌ Error al consultar CPs disponibles: {e}")
            self.consulta_cps_pendiente = False
            return False

    def mostrar_cp_disponibles(self): # Mostrar los CPs disponibles
        print("\n" + "="*60)
        print("          PUNTOS DE CARGA DISPONIBLES")
        print("="*60)
        
        if not self.consultar_cps_disponibles():
            return
        
        if not self.cps_disponibles:
            print("❌ No hay puntos de carga disponibles en este momento")
            print("Los CPs pueden estar: PARADOS, EN AVERÍA, DESCONECTADOS o SUMINISTRANDO")
            return
        
        print(f"📊 Se encontraron {len(self.cps_disponibles)} punto(s) de carga disponible(s):\n")
        print(f"{'ID CP':<15} {'UBICACIÓN':<25} {'PRECIO (€/kWh)':<15}")
        print("-" * 60)
        
        for cp in self.cps_disponibles:
            print(f"{cp['cp_id']:<15} {cp['ubicacion']:<25} {cp['precio']:<15.3f}")
        
        print("=" * 60)


    def mostrar_menu(self):
        while not self.finalizar:
            print("\n" + "="*50)
            print("          MENÚ EV_DRIVER")
            print("="*50)
            print("1. Solicitar recarga")
            print("2. Ver estado actual")
            print("3. Mostrar CP disponibles para suministrar")
            print("4. Salir")
            print("="*50)
            
            try:
                opcion = input("Seleccione una opción (1-4): ").strip()
                
                if opcion == '1':
                    if self.recarga_activa:
                        print("❌ Ya hay una recarga activa. Finalice la actual primero.")
                    else:
                        cp_id = input("Ingrese el ID del punto de carga: ").strip()
                        if cp_id:
                            print("⏳ Esperando confirmación del punto de carga...")
                            self.solicitar_recarga(cp_id)
                        else:
                            print("❌ Debe ingresar un ID de punto de carga válido")
                elif opcion == '2':
                    self.mostrar_estado()
                elif opcion == '3':
                    print("Mostrando todos los CP diponibles para suministrar...")
                    self.mostrar_cp_disponibles()
                elif opcion == '4':
                    print("👋 Saliendo del sistema...")
                    self.finalizar = True
                    break
                else:
                    print("❌ Opción no válida. Intente nuevamente.")
            
            except KeyboardInterrupt:
                print("\n👋 Saliendo del sistema...")
                self.finalizar = True
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def mostrar_estado(self):
        print("\n--- ESTADO ACTUAL ---")
        print(f"Conductor: {self.driver_id}")
        print(f"Verificado: {'✅ Sí' if self.verificado else '❌ No'}")
        print(f"Recarga activa: {'✅ Sí' if self.recarga_activa else '❌ No'}")
        if self.recarga_activa:
            print(f"CP actual: {self.cp_actual}")
        print(f"Respuestas pendientes: {self.respuestas_pendientes}")
        print("-------------------")

    def finalizar_recarga(self): # Para indicar que se finaliza la recarga tras finalizarla en el CP
        if self.recarga_activa:
            print(f"🛑 Finalizando recarga en CP: {self.cp_actual}...")
            self.recarga_activa = False
            self.cp_actual = None
            print("✅ Recarga finalizada correctamente")
        else:
            print("❌ No hay recarga activa para finalizar")

    def solicitar_recarga(self, cp_id):
        if not self.verificado:
            print("❌ Conductor no verificado. No puede solicitar recargas")
            return False
        
        mensaje = {
            'driver_id': self.driver_id,
            'cp_id': cp_id,
            'type': 'SOLICITAR_RECARGA',
            'timestamp': time.time()
        }

        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            self.productor.send('CARGA_SOLICITADA', mensaje)
            self.productor.flush() # Aseguramos que se ha enviado
            print(f"📤 Solicitud de recarga enviada del Conductor {self.driver_id} al Punto de Carga {cp_id}")
            
            # Esperamos a que el servidor responda para volver a imprimir menu
            tiempo_espera = time.time()
            while not self.respuesta_recibida and (time.time() - tiempo_espera < 30):  # Timeout de 30 segundos
                time.sleep(0.5)
            
            if not self.respuesta_recibida:
                print("❌ Timeout: No se recibió respuesta del servidor")
                self.respuestas_pendientes -= 1
            
            return True
        except Exception as e:
            self.respuestas_pendientes -= 1
            print(f"❌ Error al solicitar recarga: {e}")
            return False
    
    def detener_escucha(self):
        self.hilo_activo = False
        self.finalizar = True

def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Driver.py <IP:puerto_broker> <id_driver> [nombre_archivo_recargas]")
        sys.exit(1)
    
    servidor_kafka = sys.argv[1]
    id_driver = sys.argv[2]
    archivo = sys.argv[3] if len(sys.argv) > 3 else None

    ev_driver = EvDriver(id_driver, servidor_kafka, archivo)
    
    if not ev_driver.modo_manual:
        tiempo_inicio = time.time()
        while (ev_driver.respuestas_pendientes != 0 or not ev_driver.finalizar) and (time.time() - tiempo_inicio < 90):
            time.sleep(1)

    ev_driver.detener_escucha()
    print("\n🔌 Apagando conductor...")
    print('FIN: EV_Driver.py')

if __name__ == "__main__":
    main()