from kafka import KafkaConsumer, KafkaProducer
import json
from .config import KAFKA_SERVER

def obtener_productor(): # Crea un nuevo productor de Kafka
    return KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER], # Dirección del servidor de Kafka
        value_serializer=lambda v: json.dumps(v).encode('utf-8') # Forma de codificar los mensajes
    )

def obtener_consumidor(topico, grupo_id): # Crea un nuevo consumidor de Kafka
    return KafkaConsumer(
        topico,
        bootstrap_servers=[KAFKA_SERVER], # Dirección del servidor de Kafka
        value_deserializer=lambda v: json.loads(v.decode('utf-8')), # Forma de decodificar los mensajes
        grupo_id = grupo_id, # Identificador del grupo de consumidores
        auto_offset_reset='earliest' # Comenzar a leer desde el principio del tópico
    )