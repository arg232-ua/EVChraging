import sys
import json
from kafka import KafkaProducer, KafkaConsumer
import time # Para monitorear los eventos que van ocurriendo
import json
import threading

def obtener_productor(servidor_kafka): # Crea un nuevo productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8') # Forma de codificar los mensajes
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka): # Crea un nuevo consumidor de Kafka
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_deserializer=lambda v: json.loads(v.decode('utf-8')), # Forma de decodificar los mensajes
        grupo_id = grupo_id, # Identificador del grupo de consumidores
        auto_offset_reset='earliest' # Comenzar a leer desde el principio del tópico
    )

class EvDriver:
    def __init__(self, driver_id, servidor_kafka):
        self.driver_id = driver_id
        self.productor = obtener_productor(servidor_kafka)
        self.verificado = False

        print("PRUEBA: VOY A VERIFICAR") # borrrarrrrr #####

        if self.verificar_driver(): # Comprobamos si el conductor esta registrado en la BD

            print(f"Conductor {driver_id} inicializado y conectado a Kafka: {servidor_kafka}")

            self.escuchar_respuestas(servidor_kafka)
    
    def verificar_driver(self):
        mensaje = {
            'type': 'verificar_driver',
            'driver_id': self.driver_id,
            'timestamp': time.time() # Indico el momento exacto
        }

        try:
            self.productor.send('conductor', mensaje)
            self.productor.flush() # Aseguramos que el mensaje se envie
            print(f"Verificando si el conductor {self.driver_id} esta registrado en la Base de Datos...")
            return True
        except Exception as e:
            print(f"Error al verificar al Conductor: {e}")
            return False

    def escuchar_respuestas(self, servidor_kafka):
        def escuchar():
            consumidor = obtener_consumidor('respuestas_conductor', f'conductor-id-{self.driver_id}', servidor_kafka)

            for msg in consumidor:
                respuesta = msg.value

                if respuesta.get('driver_id') == self.driver_id:
                    if respuesta.get('exists'):
                        self.verificado = True
                        print(f"Conductor verificado correctamente. Puede solicitar recargas.")
                    else:
                        print(f"Conductor no registrado en la Base de Datos. No puede solicitar recargas.")
                        print("Contacte con un administrador para darse de alta.")
        
        # Ejecuto en segundo plano
        hilo_escucha = threading.Thread(target=escuchar, daemon=True)
        hilo_escucha.start()
    
    def solicitar_recarga(self, cp_id): # Solicito recarga a CP
        if not self.verificado: # Si el conductor no esta en la BBDD
            print("Conductor no verificado. No puede solicitar recargas")
            return False
        
        mensaje = { # Mensaje a transferir a la central
            'driver_id': self.driver_id,
            'cp_id': cp_id,
            'accion': 'solicitar_recarga',
            'timestamp': time.time()
        }

        try:
            self.productor.send('carga_solicitada', mensaje)
            self.productor.flush() # Aseguramos que el mensaje se envie
            print(f"Solicitud de recarga enviada del Conductor {self.driver_id} al Punto de Carga {cp_id}")
            return True
        except Exception as e:
            print(f"Error al solicitar recarga: {e}")
            return False
        
def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Argumentos correctos: python EV_Driver.py <IP:puerto_broker> <id_driver>")
        sys.exit(1) # Devuelve error
    
    servidor_kafka = sys.argv[1]
    id_driver = sys.argv[2]

    print(f"Prueba: {servidor_kafka}, {id_driver}") # BORRRAR

    ev_driver = EvDriver(id_driver, servidor_kafka)


if __name__ == "__main__":
    main()
