import sys
import time
import socket
import threading

def parse_host_port(hostport):
    try:
        host, port = hostport.split(":")
        return host, int(port)
    except Exception:
        raise ValueError("Formato inválido. Usa IP:PUERTO, ej. 127.0.0.1:6001")

def enviar_linea(addr, texto, timeout=1.0):
    host, port = parse_host_port(addr)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall((texto.strip() + "\n").encode("utf-8"))
            s.settimeout(timeout)
            _ = s.recv(64)
            return True
    except Exception:
        return False

def ping_engine(engine_addr, cp_id, timeout=2.0):
    host, port = parse_host_port(engine_addr)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(f"PING {cp_id}\n".encode("utf-8"))
            s.settimeout(timeout)
            resp = s.recv(16).decode("utf-8", errors="ignore").strip().upper()
            return resp == "OK"
    except Exception:   
        return False

def enviar_central(central_addr, texto, timeout=1.0):
    return enviar_linea(central_addr, texto, timeout=timeout)

def monitorizar(engine_addr, central_addr, cp_id, intervalo=2.0):
    """Monitoriza el estado del Engine mediante PING periódico."""
    ultimo_ok = ping_engine(engine_addr, cp_id)
    contador = 0

    while True:
        ok = ping_engine(engine_addr, cp_id)
        contador += 1

        if ultimo_ok and not ok:
            print(f"[EV_CP_M] [{cp_id}] AVERÍA detectada (PING=KO) -> notificar a CENTRAL")
            enviar_central(central_addr, f"MON_AVERIA {cp_id}")
        elif (not ultimo_ok) and ok:
            print(f"[EV_CP_M] [{cp_id}] RECUPERACIÓN detectada (PING=OK) -> notificar a CENTRAL")
            enviar_central(central_addr, f"MON_RECUPERADO {cp_id}")

        if contador % 5 == 0:
            estado_txt = "OK" if ok else "KO"
            print(f"[EV_CP_M] [{cp_id}] Estado actual: {estado_txt}")

        ultimo_ok = ok
        time.sleep(intervalo)

def menu_monitor(engine_addr, central_addr, cp_id):
    """Menú para simular manualmente averías y recuperaciones."""

    while True:
        ok = ping_engine(engine_addr, cp_id)
        estado_simulado = "OK" if ok else "KO"

        print("\n" + "="*45)
        print(f" Monitor del CP {cp_id}")
        print("="*45)
        print(f"Estado actual: {estado_simulado}")
        print("1. Simular AVERÍA")
        print("2. Simular RECUPERACIÓN")
        print("3. Verificar conexión con ENGINE")
        print("4. Salir")
        print("="*45)

        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == "1":
            enviar_central(central_addr, f"MON_AVERIA {cp_id}")
            print(f"[EV_CP_M] Simulación de AVERÍA enviada a CENTRAL.")
            estado_simulado = "AVERÍA"

        elif opcion == "2":
            enviar_central(central_addr, f"MON_RECUPERADO {cp_id}")
            print(f"[EV_CP_M] Simulación de RECUPERACIÓN enviada a CENTRAL.")
            estado_simulado = "OK"

        elif opcion == "3":
            ok = ping_engine(engine_addr, cp_id)
            print(f"[EV_CP_M] Verificación con Engine -> {'OK' if ok else 'KO'}")

        elif opcion == "4":
            print("[EV_CP_M] Saliendo del menú...")
            break
        else:
            print("Opción inválida, intente de nuevo.")

def main():
    if len(sys.argv) < 4:
        print("Uso: python EV_CP_M.py <IP:PUERTO_ENGINE> <IP:PUERTO_CENTRAL> <CP_ID>")
        sys.exit(1)

    engine_addr  = sys.argv[1]
    central_addr = sys.argv[2]
    cp_id = sys.argv[3]

    for a in (engine_addr, central_addr):
        try:
            parse_host_port(a)
        except ValueError as e:
            print(f"[EV_CP_M] {e}")
            sys.exit(1)

    print(f"[EV_CP_M] Monitor iniciado. CP_ID={cp_id} | Engine={engine_addr} | Central={central_addr}")

    ok = enviar_central(central_addr, f"HELLO {cp_id}")
    print(f"[EV_CP_M] HELLO Central -> {'OK' if ok else 'ERROR'}")

    hilo_mon = threading.Thread(target=monitorizar, args=(engine_addr, central_addr, cp_id), daemon=True)
    hilo_mon.start()
    print("[EV_CP_M] Monitorización automática activa (PING periódico).")

    # Menú interactivo en hilo principal
    try:
        menu_monitor(engine_addr, central_addr, cp_id)
    except KeyboardInterrupt:
        print("\n[EV_CP_M] Interrupción detectada. Saliendo...")

if __name__ == "__main__":
    main()
