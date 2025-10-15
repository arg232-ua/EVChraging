import sys
import json
from kafka import KafkaProducer, KafkaConsumer
import time # Para monitorear los eventos que van ocurriendo
import json
import threading
import os

def obtener_productor(servidor_kafka): # Crea un nuevo productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8'), # Forma de codificar los mensajes
    )

def obtener_consumidor(grupo_id, servidor_kafka): # Crea un nuevo consumidor de Kafka
    return KafkaConsumer(
        'respuestas_conductor',
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_deserializer=lambda v: json.loads(v.decode('utf-8')), # Forma de decodificar los mensajes
        group_id = grupo_id, # Identificador del grupo de consumidores
        auto_offset_reset='latest', # Comenzar a leer desde el principio del tópico
        #consumer_timeout_ms = 10000 # Timeout de 5s
    )

class EvDriver:
    def __init__(self, driver_id, servidor_kafka, archivo = None):
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

        if archivo: # Si se proporciona archivo de cargas
            self.cargar_recargas(archivo)
        else:
            self.modo_manual = True

        print("PRUEBA: VOY A VERIFICAR") # borrrarrrrr #####

        self.escuchar_respuestas()
        self.verificar_driver()

        tiempo_espera = time.time() # Espera a que llegue la respuesta
        while not self.respuesta_recibida and (time.time() - tiempo_espera < 30):  # Timeout de 30s
            time.sleep(0.5)

        if self.verificado == True:
            print(f"Conductor {driver_id} inicializado y conectado a Kafka: {servidor_kafka}")

            if self.modo_manual:
                self.solicitar_recarga(1) # Solicito recarga al CP_1 ### PROVIDSIONALLL ## AQUI ESPERARIA A QUE EL Conductor lo solicite con el HTML, CSS, JAVASCRIPT
            else:
                self.procesar_siguiente_recarga()
        else:
            print("Termino")
    
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
            'timestamp': time.time() # Indico el momento exacto
        }
        
        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            print(self.respuestas_pendientes)
            self.productor.send('conductor', mensaje)
            self.productor.flush() # Aseguramos que el mensaje se envie
            print(f"Verificando si el conductor {self.driver_id} esta registrado en la Base de Datos...")
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
                            print(f"Conductor verificado correctamente. Puede solicitar recargas.")
                        else:
                            print(f"Conductor no registrado en la Base de Datos. No puede solicitar recargas.")
                            print("Contacte con un administrador para darse de alta.")
                            self.finalizar = True
                    elif 'confirmacion' in respuesta:
                        if respuesta['confirmacion'] is True:
                            cp_id = respuesta.get('cp_id')
                            print("FALTA PONER CUANDO RECEPCIONA RESPUESTA DEL SERVIDOR")

                            if not self.modo_manual:
                                print("Esperando 4 segundos antes de la siguiente recarga...")
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()        
                        else:
                            print("FALTA PONER CUANDO RECEPCIONA RESPUESTA DEL SERVIDOR NO EXITOSA...")
                            
                            if not self.modo_manual:
                                print("Esperando 4 segundos antes del siguiente intento...")
                                time.sleep(4)
                                self.recarga_actual += 1
                                self.procesar_siguiente_recarga()
            if not self.hilo_activo: # Solo si el hilo no está activo
                self.finalizar = True
                    


        # Ejecuto en segundo plano
        hilo_escucha = threading.Thread(target=escuchar, daemon=True)
        hilo_escucha.start()
    
    def detener_escucha(self):
        self.hilo_activo = False
        self.finalizar = True

    def solicitar_recarga(self, cp_id): # Solicito recarga a CP
        if not self.verificado: # Si el conductor no esta en la BBDD
            print("Conductor no verificado. No puede solicitar recargas")
            return False
        
        mensaje = { # Mensaje a transferir a la central
            'driver_id': self.driver_id,
            'cp_id': cp_id,
            'type': 'SOLICITAR_RECARGA',
            'timestamp': time.time()
        }

        try:
            self.respuesta_recibida = False
            self.respuestas_pendientes += 1
            self.productor.send('CARGA_SOLICITADA', mensaje)
            self.productor.flush() # Aseguramos que el mensaje se envie
            print(f"Solicitud de recarga enviada del Conductor {self.driver_id} al Punto de Carga {cp_id}")
            return True
        except Exception as e:
            self.respuestas_pendientes -= 1
            print(f"Error al solicitar recarga: {e}")
            return False
        
def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Driver.py <IP:puerto_broker> <id_driver> [nombre_archivo_recargas]")
        sys.exit(1) # Devuelve error
    
    servidor_kafka = sys.argv[1]
    id_driver = sys.argv[2]
    archivo = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Prueba: {servidor_kafka}, {id_driver}") # BORRRAR

    ev_driver = EvDriver(id_driver, servidor_kafka, archivo)
    
    tiempo_inicio = time.time()
    while (ev_driver.respuestas_pendientes != 0 or not ev_driver.finalizar)  and (time.time() - tiempo_inicio < 90):
        time.sleep(1)

    ev_driver.detener_escucha()
    
    print("\nApagando conductor...")
    print('FIN PRUEBA MAIN: EV_Driver.py')

if __name__ == "__main__":
    main()
