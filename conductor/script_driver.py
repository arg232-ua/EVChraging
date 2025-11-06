import subprocess
import time
import os

def lanzar_drivers(n, kafka_broker):
    for i in range(1, n + 1):
        driver_id = f"AAA{i}"
        archivo_recargas = f"recarga_driver{i}.txt"
        ruta_archivo = os.path.join("recargas", archivo_recargas)

        if not os.path.exists(ruta_archivo):
            print(f"[AVISO] No existe el archivo de recargas para {driver_id}: {archivo_recargas}. Se lanzará en modo manual.")
            driver_cmd = f'start cmd /k python EV_Driver.py {kafka_broker} {driver_id}'
        else:
            driver_cmd = f'start cmd /k python EV_Driver.py {kafka_broker} {driver_id} {archivo_recargas}'

        subprocess.Popen(driver_cmd, shell=True)
        print(f"Lanzado {driver_id} {'con archivo' if os.path.exists(ruta_archivo) else 'en modo manual'}")
        time.sleep(0.5)  # Evitar solape de terminales

# CONFIGURA TUS PARÁMETROS
N_DRIVERS = 5
KAFKA_BROKER = "172.23.64.1:9092"

lanzar_drivers(N_DRIVERS, KAFKA_BROKER)
