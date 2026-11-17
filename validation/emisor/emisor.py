import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import os


NAME = os.environ.get("NAME", "1")
# --- CONFIGURACIÓN ---
BROKER = "<MQTT_BROKER_IP>"      # Cambia esto por la IP de tu broker (ej. "x.x.x.x" o "test.mosquitto.org")
PORT = 1883
user = "<MQTT_USER>"
password = "<MQTT_PASSWORD>"
TOPICO_CONTROL = "control/activacion"
TOPICO_DATOS = "datos/paquetes/" + NAME
PALABRA_CLAVE = "START"
TIEMPO_ESPERA = 4         # X segundos de espera entre paquete y paquete
MAX_PACKET_SIZE = 101    # Número máximo de mensajes por paquete
iniciar_envio = False

# Callbacks de MQTT
def on_connect(client, userdata, flags, rc):
    print(f"[+] Conectado al broker con código: {rc}")
    client.subscribe(TOPICO_CONTROL)
    print(f"[*] Esperando la palabra '{PALABRA_CLAVE}' en el tópico '{TOPICO_CONTROL}'...")

def on_message(client, userdata, msg):
    global iniciar_envio
    mensaje_recibido = msg.payload.decode('utf-8')
    print(f"[+] Mensaje recibido en '{msg.topic}': {mensaje_recibido}")

    if mensaje_recibido == PALABRA_CLAVE:
        print("\n[!] ¡Palabra clave recibida! Iniciando el envío de mensajes...")
        iniciar_envio = True

# Inicializar cliente
client = mqtt.Client()
client.username_pw_set(user, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

# Iniciamos el loop en segundo plano para poder ejecutar nuestro propio bucle while
client.loop_start()

try:
    while True:
        if iniciar_envio:
            # Bucle incremental de 1 a 100
            for tamaño_paquete in range(1, MAX_PACKET_SIZE):
                print(f"-> Enviando paquete de {tamaño_paquete} mensaje(s)...")
                
                # Enviar la cantidad de mensajes correspondiente al paquete actual
                for i in range(tamaño_paquete):
                    mensaje = {"emisor": NAME, "paquete": tamaño_paquete, "mensaje": i+1, "timestamp": datetime.now().isoformat()}
                    client.publish(TOPICO_DATOS, json.dumps(mensaje))
                
                # Esperar X segundos entre paquetes
                time.sleep(TIEMPO_ESPERA)
            
            print("[✓] Envío completado. Volviendo a modo de espera...")
            iniciar_envio = False # Reiniciamos por si queremos volver a activarlo enviando "START" de nuevo
            
        time.sleep(0.1) # Pequeña pausa para no saturar la CPU mientras espera

except KeyboardInterrupt:
    print("\n[-] Interrumpido por el usuario.")
finally:
    client.loop_stop()
    client.disconnect()