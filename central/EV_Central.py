import socket 
import threading


PORT = 5050
SERVER = 'localhost'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 100000

REGISTER_CP = "REGISTER_CP"
REQUEST_CHARGE = "REQUEST_CHARGE"
STATUS_UPDATE = "STATUS_UPDATE"
END_CHARGE = "END_CHARGE"



drivers = {}

cps = {}



def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} conectado.")
    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)  # recibo directamente
        msg_partido = msg.split(";")
        msg_primer = msg_partido[0]

        if not msg:
            break

        if msg_primer == REGISTER_CP:
            cp_id = msg_partido[1]
            cps[cp_id] = {"ESTADO ": "ACTIVO", "conn": conn }
        
        if msg_primer == REQUEST_CHARGE:
            driver_id = msg_partido[1]
            cp_id = msg_partido[2]
            if cps[cp_id]["estado"] == "ACTIVO":
                conn.send(f"{cp_id} esta disponible {driver_id} ".encode(FORMAT))
                conn_cp = cps[cp_id]["conn"]
                conn_cp.send(f"AUTORIZAR_CARGA al {driver_id}".encode(FORMAT))
            else:
                conn.send(f"{cp_id}  no esta disponible {driver_id} ".encode(FORMAT))
        
        if msg_primer == END_CHARGE: 
            