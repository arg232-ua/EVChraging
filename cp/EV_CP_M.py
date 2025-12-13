import sys
import time
import socket
import threading
import requests
import json

# ==========================
#  CONFIGURACIÓN REGISTRY
# ==========================

# URL del endpoint de registro del EV_Registry (API REST)
REGISTRY_URL = "https://localhost:3001/registro"

# Certificado del servidor EV_Registry (copia aquí el cert.pem del Node)
# Si el cert.pem está en otro sitio, pon la ruta correcta.
REGISTRY_CERT = "cert.pem"

# Fichero local donde guardaremos la credencial del CP
CRED_FILE = "credencial_cp.json"


# ==========================
#  FUNCIONES AUXILIARES TCP
# ==========================

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

def enviar_auth_central(central_addr, texto, timeout=2.0):
    host, port = parse_host_port(central_addr)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall((texto.strip() + "\n").encode("utf-8"))
            s.settimeout(timeout)
            resp = s.recv(1024).decode("utf-8").strip()
            return resp
    except Exception as e:
        print(f"[EV_CP_M] Error enviando AUTH a Central: {e}")
        return None

# ==========================
#  FUNCIONES REGISTRO / CRED
# ==========================

def guardar_credencial(id_cp, credencial):
    """Guarda en disco la credencial del CP."""
    data = {"id_cp": id_cp, "credencial": credencial}
    with open(CRED_FILE, "w") as f:
        json.dump(data, f)
    print(f"[EV_CP_M] Credencial guardada localmente ({CRED_FILE}): {credencial}")


def cargar_credencial():
    """Carga la credencial del fichero, si existe. Devuelve dict o None."""
    try:
        with open(CRED_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[EV_CP_M] Error leyendo {CRED_FILE}: {e}")
        return None


def registrar_cp_en_registry(id_cp):
    """
    Realiza un POST HTTPS al EV_Registry para registrar el CP.
    Devuelve True si el registro ha ido bien y guarda la credencial.
    """

    payload = {
    "cp_logico": int(id_cp),  # 🔑 CLAVE: CP lógico
    "id_central": "0039051",
    "ubicacion_punto_recarga": f"CP {id_cp} – EPS",
    "precio": 0.35,
    "estado": "DESCONECTADO"
    }


    print(f"[EV_CP_M] Registrando CP {id_cp} en EV_Registry...")

    try:
        # verify=REGISTRY_CERT asegura canal cifrado y confianza en el cert autofirmado
        resp = requests.post(REGISTRY_URL, json=payload, verify=False)
        data = resp.json()

        if resp.status_code != 200:
            print(f"[EV_CP_M] Error HTTP en registro: {resp.status_code}, respuesta: {data}")
            return False

        if "credencial" not in data:
            print(f"[EV_CP_M] Respuesta de Registry sin credencial: {data}")
            return False

        cred = data["credencial"]
        guardar_credencial(id_cp, cred)
        print(f"[EV_CP_M] Registro en EV_Registry OK. ID_CP_BD={data.get('id_punto_recarga')}  Credencial={cred}")
        return True

    except requests.exceptions.SSLError as e:
        print("[EV_CP_M] Error SSL con EV_Registry (revisa REGISTRY_CERT):", e)
        return False
    except Exception as e:
        print("[EV_CP_M] Error de conexión HTTPS a EV_Registry:", e)
        return False


# ==========================
#  MONITORIZACIÓN
# ==========================

def monitorizar(engine_addr, central_addr, cp_id, intervalo=2.0):
    ultimo_ok = ping_engine(engine_addr, cp_id)
    contador = 0

    while True:
        ok = ping_engine(engine_addr, cp_id)
        contador += 1

        if ultimo_ok and not ok:
            # Paso de OK -> KO
            print(f"[EV_CP_M] [{cp_id}] AVERÍA detectada (PING=KO) -> notificar a CENTRAL")
            enviar_central(central_addr, f"EN_AVERIA {cp_id}")
        elif (not ultimo_ok) and ok:
            # Paso de KO -> OK
            print(f"[EV_CP_M] [{cp_id}] RECUPERACIÓN detectada (PING=OK) -> notificar a CENTRAL")
            enviar_central(central_addr, f"EN_RECUPERADO {cp_id}")

        if contador % 5 == 0:
            estado_txt = "OK" if ok else "KO"
            print(f"[EV_CP_M] [{cp_id}] Estado actual (PING): {estado_txt}")

        ultimo_ok = ok
        time.sleep(intervalo)


def menu_monitor(engine_addr, central_addr, cp_id):

    while True:
        ok = ping_engine(engine_addr, cp_id)
        estado_simulado = "OK" if ok else "KO"

        print("\n" + "="*45)
        print(f" Monitor del CP {cp_id}")
        print("="*45)
        print(f"Estado actual (PING): {estado_simulado}")
        print("1. Simular AVERÍA Engine")
        print("2. Simular AVERÍA Monitor")
        print("3. Simular RECUPERACIÓN Engine")
        print("4. Simular RECUPERACIÓN Monitor")
        print("5. Verificar conexión con ENGINE")
        print("6. Salir")
        print("="*45)

        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            enviar_central(central_addr, f"EN_AVERIA {cp_id}")
            print(f"[EV_CP_M] Simulación de AVERÍA de Engine enviada a CENTRAL.")
        elif opcion == "2":
            enviar_central(central_addr, f"MON_AVERIA {cp_id}")
            print(f"[EV_CP_M] Simulación de AVERÍA de Monitor enviada a CENTRAL.")
        elif opcion == "3":
            enviar_central(central_addr, f"EN_RECUPERADO {cp_id}")
            print(f"[EV_CP_M] Simulación de RECUPERACIÓN de Engine enviada a CENTRAL.")
        elif opcion == "4":
            enviar_central(central_addr, f"MON_RECUPERADO {cp_id}")
            print(f"[EV_CP_M] Simulación de RECUPERACIÓN de Monitor enviada a CENTRAL.")
        elif opcion == "5":
            ok = ping_engine(engine_addr, cp_id)
            print(f"[EV_CP_M] Verificación con Engine -> {'OK' if ok else 'KO'}")
        elif opcion == "6":
            print("[EV_CP_M] Saliendo del menú...")
            break
        else:
            print("Opción inválida, intente de nuevo.")


# ==========================
#  MAIN
# ==========================

def main():
    if len(sys.argv) < 4:
        print("Uso: python EV_CP_M.py <IP:PUERTO_ENGINE> <IP:PUERTO_CENTRAL> <CP_ID>")
        sys.exit(1)

    engine_addr  = sys.argv[1]
    central_addr = sys.argv[2]
    cp_id        = sys.argv[3]

    # Validar formatos IP:PUERTO
    for a in (engine_addr, central_addr):
        try:
            parse_host_port(a)
        except ValueError as e:
            print(f"[EV_CP_M] {e}")
            sys.exit(1)

    print(f"[EV_CP_M] Monitor iniciado. CP_ID={cp_id} | Engine={engine_addr} | Central={central_addr}")

    # 1) Comprobar si ya tenemos credencial guardada
    cred = cargar_credencial()
    if not cred:
        print("[EV_CP_M] No existe credencial local. Registrando CP en EV_Registry (HTTPS)...")
        if not registrar_cp_en_registry(cp_id):
            print("[EV_CP_M] Registro en EV_Registry FALLIDO. No se puede iniciar el CP.")
            sys.exit(1)
        cred = cargar_credencial()

    id_cp_bd = str(cred["id_cp"])
    credencial = cred["credencial"]
    print(f"[EV_CP_M] Credencial cargada. ID_CP_BD={id_cp_bd}")

    # 2) AUTH a CENTRAL
    auth_msg = f"AUTH {id_cp_bd} {credencial}"
    resp = enviar_auth_central(central_addr, f"AUTH {id_cp_bd} {credencial}")
    print(f"[EV_CP_M] Respuesta Central: {resp}")

    if resp and resp.startswith("AUTH_OK"):
        _, clave = resp.split(maxsplit=1)
        with open("clave_simetrica.json", "w") as f:
            json.dump({"clave_simetrica": clave}, f)
        print("[EV_CP_M] Autenticación correcta. Clave simétrica guardada.")
    else:
        print("[EV_CP_M] Autenticación FALLIDA con Central.")
        sys.exit(1)



    # 3) Lanzar hilo de monitorización automática
    hilo_mon = threading.Thread(
        target=monitorizar,
        args=(engine_addr, central_addr, cp_id),
        daemon=True
    )
    hilo_mon.start()
    print("[EV_CP_M] Monitorización automática activa (PING periódico).")

    # 4) Menú interactivo
    try:
        menu_monitor(engine_addr, central_addr, cp_id)
    except KeyboardInterrupt:
        print("\n[EV_CP_M] Interrupción detectada. Saliendo...")


if __name__ == "__main__":
    main()
