import subprocess
import time
import os
import sys

def lanzar_drivers(n, kafka_broker):
    for i in range(1, n + 1):
        driver_id = f"AAA{i}"
        archivo_recargas = f"recarga_driver{i}.txt"
        ruta_archivo = os.path.join("recargas", archivo_recargas)

        if not os.path.exists(ruta_archivo):
            print(f"[AVISO] No se ha seleccionado el archivo de recargas para {driver_id}: {archivo_recargas}. Se lanzará en modo manual.")
            # El modo de recargas on archivo lo hemos implementado solo de forma manual, para que en la corrección se pueda ver todo sin colapsar la información
            driver_cmd = f'start cmd /k python EV_Driver.py {kafka_broker} {driver_id}'
        else:
            driver_cmd = f'start cmd /k python EV_Driver.py {kafka_broker} {driver_id} {archivo_recargas}'

        subprocess.Popen(driver_cmd, shell=True)
        print(f"Lanzado {driver_id} {'con archivo' if os.path.exists(ruta_archivo) else 'en modo manual'}")
        time.sleep(0.5)  # Evitar solape de terminales

def main():
    if len(sys.argv) != 3:
        print("ERROR: Argumentos incorrectos")
        print("Uso: python script_driver.py <IP:puerto_broker> <Número_de_Drivers_a_inicializar>")
        # Ejemplo: python script_driver.py <IP_del_PC_de_la_Central:9092> <10>
        sys.exit(1)

    servidor_kafka = sys.argv[1]
    numero_drivers = sys.argv[2]

    N_DRIVERS = int(numero_drivers)
    KAFKA_BROKER = servidor_kafka

    lanzar_drivers(N_DRIVERS, KAFKA_BROKER)


if __name__ == "__main__":
    main()