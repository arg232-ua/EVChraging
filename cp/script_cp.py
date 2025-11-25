import subprocess
import time
import sys

def lanzar_cps(n, kafka_broker, central_host, precio_base, port_base):
    for i in range(1, n + 1):
        cp_id = i
        puerto_engine = port_base + i

        # Verifica si el puerto está disponible
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', puerto_engine))
        sock.close()
        
        if result == 0:
            print(f"Puerto {puerto_engine} en uso, usando alternativo")
            puerto_engine += 100  # Usa puerto alternativo
        
        # Ubicación personalizada por CP
        ubicacion = f"Zona {i} – EPS 4 – Universidad de Alicante"

        # Comando para EV_CP_E en nueva terminal
        engine_cmd = f"start cmd /k python EV_CP_E.py {kafka_broker} {cp_id} \"{ubicacion}\" {precio_base} {puerto_engine}"
        subprocess.Popen(engine_cmd, shell=True)
        print(f"Lanzado EV_CP_E CP {cp_id} en puerto {puerto_engine} con ubicación '{ubicacion}'")
        time.sleep(0.5)  # Espera para evitar que las terminales se solapen

        # Comando para EV_CP_M en nueva terminal
        monitor_cmd = f"start cmd /k python EV_CP_M.py {central_host}:{puerto_engine} {central_host}:7001 {cp_id}"
                                                        # cambiar
        subprocess.Popen(monitor_cmd, shell=True)
        print(f"Lanzado EV_CP_M CP {cp_id}")
        time.sleep(0.5)

def main():
    if len(sys.argv) != 4:
        print("ERROR: Argumentos incorrectos")
        print("Uso: python script_cp.py <IP:puerto_broker> <IP_Central> <Número_de_CPs_a_inicializar>")
        # Ejemplo: python script_cp.py <IP_del_PC_de_los_CPS:9092> <IP_deL_PC_de_la_central> <10>
        sys.exit(1)

    servidor_kafka = sys.argv[1]
    central = sys.argv[2]
    numero_cps = sys.argv[3]

    N_CP = int(numero_cps)
    KAFKA_BROKER = servidor_kafka
    CENTRAL_HOST = central
    PRECIO_BASE = 0.35
    PORT_BASE = 6000  # El primero será 6001, luego 6002, ...


    lanzar_cps(N_CP, KAFKA_BROKER, CENTRAL_HOST, PRECIO_BASE,PORT_BASE)

if __name__ == "__main__":
    main()