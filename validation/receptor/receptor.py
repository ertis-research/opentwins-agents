import paho.mqtt.client as mqtt
import csv
from datetime import datetime
import pandas as pd
import json
import os
# --- CONFIGURACIÓN ---
NAME = os.environ.get("NAME", "1")
BROKER = "<MQTT_BROKER_IP>"
user = "<MQTT_USER>"
password = "<MQTT_PASSWORD>"
PORT = 1883
TOPICO_DATOS = "datos/paquetes/" + NAME
ARCHIVO_DATASET = "dataset_mensajes"
CONTADOR = 0
df = []
topics = [
    (TOPICO_DATOS, 0),
    ("control/activacion", 0)
]


def on_connect(client, userdata, flags, rc):
    print(f"[+] Conectado al broker para recibir datos. Código: {rc}")
    # client.subscribe(TOPICO_DATOS)
    # client.subscribe("control/activacion")  # Suscribimos también al tópico de control para detectar la palabra "SAVE"
    
    client.subscribe(topics)
    print(f"[*] Escuchando en el tópico '{TOPICO_DATOS}' y guardando en '{ARCHIVO_DATASET}'...")

def on_message(client, userdata, msg):
    global CONTADOR
    global df
    message = msg.payload.decode('utf-8')
    print(message)
    
    if message == "START":
        print("\n[!] ¡Palabra clave 'START' recibida! No hago nada...")
    elif message == "SAVE":
        dataframe = pd.DataFrame(df)
        print(dataframe)
        dataframe.to_csv(ARCHIVO_DATASET+"_"+NAME+"_"+str(CONTADOR)+".csv", index=False)
        # pd.DataFrame(df).to_csv(ARCHIVO_DATASET+"_"+NAME+"_"+str(CONTADOR)+".csv", index=False, mode='w', header=True)
        CONTADOR += 1
    else:
        print("Mensaje por topico de datos recibido. Procesando...")
        mensaje_recibido = json.loads(message)
        # Capturamos el timestamp en el momento de la llegada
        timestamp_llegada = datetime.now().isoformat()
        mensaje_recibido["timestamp_llegada"] = timestamp_llegada
        print(mensaje_recibido)
        
        df.append(mensaje_recibido)
        
    

client = mqtt.Client()
client.username_pw_set(user, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

try:
    # loop_forever bloquea el hilo principal y se encarga de mantener la conexión y recibir mensajes
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[-] Receptor detenido por el usuario.")
    client.disconnect()