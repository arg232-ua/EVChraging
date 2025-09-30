# Para ahorrar código repetido
import json
import socket

# Para obtener la IP del servidor
def get_server_ip():
    try:
        with open('server_ip.txt', 'r') as f: # Encuentro el archivo
            ip = f.read().strip() # Leo y guardo la IP
            print(f"Usando el servidor: {ip}")
            return ip # Devuelvo la IP
    except FileNotFoundError:
        ip = input("Introduce la IP del PC Central: ") # Pido que se introduzca la IP
        with open('server_ip.txt', 'w') as f: # Creo el fichero
            f.write(ip) # Almaceno la IP
        return ip # Devuelvo la IP

# Configuración IP y Kafka
SERVER_IP = get_server_ip() # Obtengo la IP del servidor
KAFKA_SERVER = f"{SERVER_IP}:9092" # Dirección del servidor Kafka

# Configuración BBDD
DB_CONFIG = {
    'host': SERVER_IP,
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'evcharging'
}