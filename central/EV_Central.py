import socket 
import threading
import time


PORT = 5050
SERVER = 'localhost'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 100000

REGISTER_CP = "REGISTER_CP"
REQUEST_CHARGE = "REQUEST_CHARGE"

END_CHARGE = "END_CHARGE"
AVISO_RECUPERADO = "AVISO_RECUPERADO"


drivers = {}

cps = {}



def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} conectado.")
    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)  # recibo directamente
        msg_partido = msg.split(";")
        msg_primer = msg_partido[0]

        

        if msg_primer == REGISTER_CP:
            cp_id = msg_partido[1]
            cps[cp_id] = {"ESTADO": "ACTIVO", "conn": conn }
        
        if not msg:
            if cp_id in cps:
                print(f"[DESCONECTADO] {cp_id} se ha desconectado")
                cps[cp_id]["ESTADO"] = "DESCONECTADO"


        if msg_primer == REQUEST_CHARGE:
            driver_id = msg_partido[1]
            cp_id = msg_partido[2]
            if cps[cp_id]["ESTADO"] == "ACTIVO":
                conn.send(f"{cp_id} esta disponible {driver_id}".encode(FORMAT))
                conn_cp = cps[cp_id]["conn"]    
                conn_cp.send(f"AUTORIZAR_CARGA al {driver_id}".encode(FORMAT))
                cps[cp_id]["ESTADO"] = "SUMINISTRANDO"

            elif cps[cp_id]["ESTADO"] == "PARADO":
                conn.send(f"{cp_id} no esta disponible {driver_id} ".encode(FORMAT))
            
            elif cps[cp_id]["ESTADO"] == "AVERIADO":
                conn.send(f"{cp_id} no esta disponible {driver_id} ".encode(FORMAT))
            
            elif cps[cp_id]["ESTADO"] == "DESCONECTADO":
                conn.send(f"{cp_id} no esta disponible {driver_id} ".encode(FORMAT))
        
        if msg_primer == END_CHARGE:
            cp_id = msg_partido[1]
            conn_cp = cps[cp_id]["conn"]
            conn_cp.send(f"Estado del {cp_id} Pasando de estado SUMINISTRANDO a ACTIVO en 4 segundos".encode(FORMAT))
            time.sleep(4)
            cps[cp_id]["ESTADO"] = "ACTIVO"
            conn_cp.send(f"{cp_id} vuelve a estar ACTIVO")


        if msg_primer == "AVISO_AVERIA":
            cp_id = msg_partido[1]
            if cp_id in cps:
                estado_anterior = cps[cp_id]["ESTADO"]
                if estado_anterior == "DESCONECTADO":
                    print(f"[CENTRAL] Ignorado AVISO_AVERIA de {cp_id} porque está DESCONECTADO.")
                else:
                    cps[cp_id]["ESTADO"] = "AVERIADO"
                    conn_cp = cps[cp_id]["conn"]
                    if estado_anterior == "SUMINISTRANDO":
                        conn_cp.send(f"[CENTRAL] {cp_id} ha sido AVERIADO durante la carga. ¡DETENER SUMINISTRO!".encode(FORMAT))
                        print(f"[CENTRAL] {cp_id} estaba cargando. Suministro interrumpido por avería.")
                    else:
                        conn_cp.send(f"[CENTRAL] {cp_id} ha sido marcado como AVERIADO.".encode(FORMAT))
                        print(f"[CENTRAL] {cp_id} marcado como AVERIADO.")


        if msg_primer == AVISO_RECUPERADO:
            cp_id = msg_partido[1]
            if cp_id in cps["ESTADO"] == "AVERIADO":
                conn_cp = cps[cp_id]["conn"] 
                conn_cp.send(f"{cp_id} actualmente disponible".encode(FORMAT))
                cps[cp_id]["ESTADO"] = "ACTIVO"
            elif cp_id in cps:
                conn_cp.send(f"{cp_id} ha enviado recuperación, pero no estaba en AVERIADO".encode(FORMAT))

        