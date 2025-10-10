from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import sys
import time
<<<<<<< HEAD
import argparse
=======
import mysql.connector
>>>>>>> 3a62e3cb549c06380a1666381288ae1846ad9fd0

def obtener_productor(servidor_kafka): # Crea un nuevo productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8'), # Forma de codificar los mensajes
    )

<<<<<<< HEAD
PORT = 5050
#SERVER = 'localhost'
#ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 100000
#PORT = 5050
=======
def obtener_consumidor(topico, grupo_id, servidor_kafka): # Crea un nuevo consumidor de Kafka
    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka], # Dirección del servidor de Kafka
        value_deserializer=lambda v: json.loads(v.decode('utf-8')), # Forma de decodificar los mensajes
        group_id = grupo_id, # Identificador del grupo de consumidores
        auto_offset_reset='earliest', # Comenzar a leer desde el principio del tópico
    )
>>>>>>> 3a62e3cb549c06380a1666381288ae1846ad9fd0

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

<<<<<<< HEAD
def get_args():
    parser = argparse.ArgumentParser(description="EV Charging CENTRAL")
    parser.add_argument("puerto", type=int, help="Puerto de escucha de la CENTRAL")
    parser.add_argument("broker", type=str, help="IP:puerto del Broker")
    parser.add_argument("--bbdd", type=str, default=None, help="IP:puerto de la base de datos (opcional)")
    return parser.parse_args()

args = get_args()

# 🔧 Extraer IPs y puertos del broker y base de datos
broker_ip, broker_port = args.broker.split(":")
bbdd_ip, bbdd_port = (args.bbdd.split(":") if args.bbdd else (None, None))

# 🔧 Usar el puerto recibido como argumento
SERVER = '0.0.0.0'
PORT = args.puerto
ADDR = (SERVER, PORT)

# 🔧 Mostrar configuración de inicio
print("[CENTRAL] Arrancando EV_Central...\n")
print(f"[CENTRAL] Puerto de escucha: {PORT}")
print(f"[CENTRAL] Broker: {broker_ip}:{broker_port}")
if args.bbdd:
    print(f"[CENTRAL] Base de datos: {bbdd_ip}:{bbdd_port}")
else:
    print("[CENTRAL] Base de datos: No usada")
print()

# 🔌 Crear el socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
=======
class EV_Central:
    def __init__(self, servidor_kafka, servidor_bd):
        self.servidor_kafka = servidor_kafka
        self.servidor_bd = servidor_bd
        self.productor = obtener_productor(servidor_kafka)
        self.cps = {}
        self.conexion_bd = conectar_bd(servidor_bd)
>>>>>>> 3a62e3cb549c06380a1666381288ae1846ad9fd0

        print(f"Central inicializada y conectada a Kafka: {servidor_kafka} y BD: {servidor_bd}")

    def verifico_driver(self, driver_id):
        if self.conexion_bd is None:
            print("No hay conexion a la BD")
            return False
        else:
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
        consumidor = obtener_consumidor('conductor', 'central', self.servidor_kafka)
        print("CENTRAL: Escuchando peticiones...")

        for msg in consumidor:
            peticion = msg.value
            tipo = peticion.get('type')

            if tipo == 'VERIFICAR_DRIVER':
                driver_id = peticion.get('driver_id')
                print(f"Verificando si el conductor {driver_id} esta registrado en la Base de Datos...")
                
                respuesta = {
                    'driver_id': driver_id,
                    'exists': self.verifico_driver(driver_id)
                }

                self.productor.send('respuestas_conductor', respuesta)
                self.productor.flush() # Aseguramos que el mensaje se envie
                print(f"Mensaje enviado al conductor: {driver_id}")

    def escuchar_peticiones_recarga(self):
        consumidor = obtener_consumidor('conductor', 'central', self.servidor_kafka)
        print("CENTRAL: Escuchando peticiones...")

#        for msg in consumidor:
#            peticion = msg.value
#            tipo = peticion.get('type')

#            if tipo == 'VERIFICAR_DRIVER':
#                driver_id = peticion.get('driver_id')
#                print(f"Verificando si el conductor {driver_id} esta registrado en la Base de Datos...")
                
#                respuesta = {
#                    'driver_id': driver_id,
#                    'exists': self.verifico_driver(driver_id)
#                }

#                self.productor.send('respuestas_conductor', respuesta)
#                self.productor.flush() # Aseguramos que el mensaje se envie
#                print(f"Mensaje enviado al conductor: {driver_id}")

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

<<<<<<< HEAD
def start():
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER}:{PORT}")
    threading.Thread(target=comandos, daemon=True).start()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CONEXIONES ACTIVAS] {threading.active_count() - 1}")

start()
=======
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
>>>>>>> 3a62e3cb549c06380a1666381288ae1846ad9fd0
