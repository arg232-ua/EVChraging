import threading
import time
import json
import requests
from datetime import datetime

class WeatherControlOffice:
    def __init__(self, config_file = "weather_config.json", api_central = "http://localhost:3000"):
        self.config_file = config_file
        self.api_central = api_central
        self.api_open_weather = "e7abad131d41796211d63d8c20bc59d1" # Api de la web OpenWeather
        self.localizaciones = self.cargar_localizaciones()
        self.localizaciones_alertadas = set()

    def cargar_localizaciones(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                return config.get("locations", [])
        except FileNotFoundError:
            print("Archivo de configuración no encontrado.")
            return []
        
    def añadir_localizaciones(self, city, country, cp_id): # Añadir nueva localización
        self.localizaciones.append({"city": city, "country": country, "cp_id": cp_id})
        self.guardar_localizaciones()
    
    def guardar_localizaciones(self): # Guardar localizaciones en archivo
        config = {"locations": self.localizaciones}
        with open(self.config_file, 'w') as file:
            json.dump(config, file, indent = 2)

    def get_temperature(self, city, country): # Obtener la temperatura
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={self.api_open_weather}&units=metric"
        try:
            response = requests.get(url, timeout = 10)
            data = response.json()

            if response.status_code == 200:
                temp = data["main"]["temp"] # Saco solo la temperatura del JSON
                print(f"[INFO]: Temperatura actual en {city}, {country}: {temp}ºC")
                return temp
            else:
                print(f"Error al obtener datos para {city}, {country}: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Error en la conexión para {city}: {e}")
            return None

    def notificar_central(self, cp_id, estado, temperatura): # Notificar central sobre alertas
        url = f"{self.api_central}/weather-alert"

        mensaje = {"cp_id": cp_id, "alert_type": estado, "temperature": temperatura, "timestamp": datetime.now().isoformat()}
        try:
            response = requests.post(url, json = mensaje, timeout = 10)
            if response.status_code == 200:
                print(f"Notificación enviada a la central para CP_ID {cp_id} con estado {estado}.")
            else:
                print(f"Error al notificar a la central para CP_ID {cp_id}: {response.text}")
        except Exception as e:
            print(f"Error en la conexión con la central para CP_ID {cp_id}: {e}")


    def verificar_localizaciones(self): # para guardar la última temperatura conocida de cada CP
        if not hasattr(self, 'ultimas_temperaturas'):
            self.ultimas_temperaturas = {}
        
        for loc in self.localizaciones:
            temp = self.get_temperature(loc["city"], loc["country"])

            if temp is not None:
                cp_id = loc["cp_id"]
                
                # Notificar SIEMPRE el cambio de temperatura (nuevo)
                if cp_id in self.ultimas_temperaturas:
                    temp_anterior = self.ultimas_temperaturas[cp_id]
                    # Notificar si la temperatura cambió más de 0.5°C (evita notificaciones por cambios mínimos)
                    if abs(temp - temp_anterior) >= 0.5:
                        print(f"[TEMPERATURA] CP {cp_id}: {temp_anterior}°C → {temp}°C")
                        self.notificar_central(cp_id, "cambio_temperatura", temp)
                else:
                    # Primera vez que vemos este CP
                    print(f"[TEMPERATURA] CP {cp_id}: primera medición {temp}°C")
                    self.notificar_central(cp_id, "cambio_temperatura", temp)
                
                # Guardar la nueva temperatura
                self.ultimas_temperaturas[cp_id] = temp
                
                # alerta por debajo de 0°C
                if temp < 0 and cp_id not in self.localizaciones_alertadas:
                    print(f"[ALERTA]: La ciudad {loc['city']} con CP_ID {cp_id} perteneciente a esa ciudad, se encuentra a {temp} ºC.")
                    self.notificar_central(cp_id, "bajo_zero", temp)
                    self.localizaciones_alertadas.add(cp_id)
                elif temp >= 0 and cp_id in self.localizaciones_alertadas:
                    print(f"[INFO]: Alerta finalizada en la ciudad {loc['city']} con CP_ID {cp_id} perteneciente a esa ciudad. Temperatura actual: {temp} ºC.")
                    self.notificar_central(cp_id, "normal", temp)
                    self.localizaciones_alertadas.remove(cp_id)

    def comenzar_monitorizacion(self, intervalo = 4): # Iniciar monitoreo continuo con intervalo de 4 segundos
        print(f"EV_W Iniciado. Monitoreando {len(self.localizaciones)} localizaciones cada {intervalo} segundos.")

        def monitor():
            while True:
                self.verificar_localizaciones()
                time.sleep(intervalo)
        
        # Ejecutar en hilo separado
        monitor_thread = threading.Thread(target = monitor, daemon = True)
        monitor_thread.start()
        return monitor_thread

def main():
    ev_w = WeatherControlOffice()
    print("== Weather Control Office ==")
    print("1. Iniciar monitoreo automático")
    print("2. Añadir nueva localización")
    print("3. Ver localizaciones actuales")
    print("4. Verificar temperatura ahora")
    print("5. Salir")

    ev_w.comenzar_monitorizacion()

    while True:
        opcion = input("\nSeleccione una opción:")
        
        if opcion == "1":
            print("Monitoreo automático iniciado")
        elif opcion == "2":
            city = input("Ingrese la ciudad:")
            country = input("Ingrese el país (ej: ES):")
            cp_id = input("Ingrese el ID del punto de carga (CP_ID):")
            ev_w.añadir_localizaciones(city, country, cp_id)
            print(f"Localización {city}, {country} añadida para CP_ID {cp_id}.")
        elif opcion == "3":
            print("Localizaciones actuales:")
            for loc in ev_w.localizaciones:
                print(f"- {loc['city']}, {loc['country']} (CP_ID: {loc['cp_id']})")
        elif opcion == "4":
            ev_w.verificar_localizaciones()
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Monitoreo en ejecución... (Ctrl+C para salir)")
            
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                print("\nSaliendo...")
                break


if __name__ == "__main__":
    main()