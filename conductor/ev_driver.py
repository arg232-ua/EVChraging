from compartido.config import KAFKA_SERVER
from compartido.kafka_helper import obtener_productor, obtener_consumidor
import time # Para monitorear los eventos que van ocurriendo
import json
import threading

class EvDriver:
    def __init__(self, driver_id):
        self.driver_id = driver_id
        self.productor = obtener_productor()
        self.verificado = False

        self.verificar_driver() # Comprobamos si el conductor esta registrado en la BD

        print(f"Conductor {driver_id} inicializado y conectado a Kafka: {KAFKA_SERVER}")

        self.escuchar_respuestas()
    
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
        except Exception as e:
            print(f"Error al verificar al Conductor: {e}")

    def escuchar_respuestas(self):
        def escuchar():
            consumidor = obtener_consumidor('respuestas_conductor', f'conductor-id-{self.driver_id}')

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
    
    def solicitar_recarga(self, cp_id):
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
