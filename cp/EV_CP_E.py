#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import threading


# -----------------------------
# Tópicos Kafka
TOPIC_REGISTROS = "registros_cp"
TOPIC_COMANDOS  = "comandos_cp"
TOPIC_ESTADO    = "estado_cp"
TOPIC_MONITOR   = "monitor_cp"
# -----------------------------

ESTADOS_VALIDOS = {"ACTIVADO", "PARADO", "AVERIA", "SUMINISTRANDO", "DESCONECTADO"}


# === Utilidades Kafka (mismo patrón que EV_Driver) ===
def obtener_productor(servidor_kafka):

    return KafkaProducer(
        bootstrap_servers=[servidor_kafka],
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        linger_ms=10,
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

def obtener_consumidor(topico, grupo_id, servidor_kafka, auto_offset_reset="latest"):

    return KafkaConsumer(
        topico,
        bootstrap_servers=[servidor_kafka],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id=grupo_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )

# === Clase principal del CP ===
class EV_CP:

    def __init__(self, servidor_kafka, cp_id, ubicacion="N/A", precio_eur_kwh=0.35):
        self.servidor_kafka = servidor_kafka
        self.cp_id = cp_id
        self.ubicacion = ubicacion
        self.precio = float(precio_eur_kwh)
        self.estado = "ACTIVADO"   # Estado inicial

        self.productor = None

    def conectar(self):

        self.productor = obtener_productor(self.servidor_kafka)

        for _ in range(10):
            if self.productor.bootstrap_connected():
                print(f"[EV_CP_E] Conectado a Kafka en {self.servidor_kafka}")
                return True
            time.sleep(0.2)

        print(f"[EV_CP_E] No fue posible conectar con Kafka en {self.servidor_kafka}")
        return False

    def registrar_cp(self):

        datos = {
            "tipo": "REGISTRO_CP",
            "ts": datetime.utcnow().isoformat(),
            "cp_id": self.cp_id,
            "ubicacion": self.ubicacion,
            "estado_inicial": self.estado
        }
        self.productor.send(TOPIC_REGISTROS, key=self.cp_id, value=datos)
        self.productor.flush()
        print(f"[EV_CP_E] Registrado CP '{self.cp_id}' en tópico '{TOPIC_REGISTROS}'.")

    def enviar_estado(self, nuevo_estado: str, motivo: str = ""):

        if nuevo_estado not in ESTADOS_VALIDOS:
            print(f"[EV_CP_E] Estado ignorado (no válido): {nuevo_estado}")
            return

        self.estado = nuevo_estado
        datos = {
            "ts": datetime.utcnow().isoformat(),
            "cp_id": self.cp_id,
            "estado": self.estado,
            "motivo": motivo,
            "precio_eur_kwh": self.precio
        }
        self.productor.send(TOPIC_ESTADO, key=self.cp_id, value=datos)
        self.productor.flush()
        print(f"[EV_CP_E] Estado publicado -> {self.cp_id}: {self.estado} ({motivo})")

        def _handle_command(self, msg: dict):
            cmd = (msg.get("cmd") or "").upper()
            if cmd == "PARAR":
                self.enviar_estado("PARADO", motivo="Central ordena PARAR")
            elif cmd == "REANUDAR":
                self.enviar_estado("ACTIVADO", motivo="Central ordena REANUDAR")
            elif cmd == "AVERIA":
                self.enviar_estado("AVERIA", motivo="Central marca AVERIA")
            elif cmd == "RECUPERADO":
                self.enviar_estado("ACTIVADO", motivo="Central marca RECUPERADO")
            else:
                print(f"[EV_CP_E] Comando no reconocido (ignorado): {cmd}")

    def escuchar_comandos(self):
  
        try:
            consumidor = obtener_consumidor(
                topico=TOPIC_COMANDOS,
                grupo_id=f"cp_{self.cp_id}",
                servidor_kafka=self.servidor_kafka,
                auto_offset_reset="latest"
            )
            print(f"[EV_CP_E] Escuchando comandos en '{TOPIC_COMANDOS}' (grupo=cp_{self.cp_id})...")
            for record in consumidor:
                msg = record.value
                if not isinstance(msg, dict):
                    continue
                destino = msg.get("cp_id")
                if destino not in (self.cp_id, "ALL"):
                    continue
                self._handle_command(msg)
        except Exception as e:
            print(f"[EV_CP_E] Error en escuchar_comandos: {e}")


def main():
    if len(sys.argv) < 3:
        print("ERROR: Argumentos incorrectos")
        print("Uso: python EV_CP_E.py <IP:puerto_broker> <CP_ID> [<UBICACION>] [<PRECIO_EUR_KWH>]")
        sys.exit(1)

    servidor_kafka = sys.argv[1]
    cp_id = sys.argv[2]
    ubicacion = sys.argv[3] if len(sys.argv) >= 4 else "N/A"

    print(f"[EV_CP_E] Broker: {servidor_kafka} | CP_ID: {cp_id} | Ubicación: {ubicacion}")

    cp = EV_CP(servidor_kafka, cp_id, ubicacion)

    try:
        if not cp.conectar():
            sys.exit(2)


        cp.registrar_cp()
                
        cp.enviar_estado(cp.estado, motivo="Arranque CP")

       
        hilo_cmd = threading.Thread(target=cp.escuchar_comandos, daemon=True)
        hilo_cmd.start()

        print("[EV_CP_E] Paso 3 OK: CP registrado. (Aún sin escuchar comandos ni publicar estado). Ctrl+C para salir.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[EV_CP_E] Saliendo…")
    finally:
        try:
            if cp.productor is not None:
                cp.productor.flush(1.0)
                cp.productor.close(1.0)
        except Exception:
            pass

if __name__ == "__main__":
    main()
