import time
from datetime import datetime
import paho.mqtt.client as mqtt

# 1. Medir el instante de tiempo nada más arrancar
start_time = time.time()*1000
start_dt = start_time

# Configuración del broker MQTT de prueba
BROKER = "<MQTT_BROKER_IP>"      # Cambia esto por la IP de tu broker (ej. "x.x.x.x" o "test.mosquitto.org")
PORT = 1883

end_time = None

def on_connect(client, userdata, flags, reason_code, properties):
    global end_time
    if reason_code == 0:
        end_time = time.time()*1000
    else:
        print(f"❌ Error al conectar al broker MQTT: {reason_code}")





# Inicializar el cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set("<MQTT_USER>", "<MQTT_PASSWORD>")
client.on_connect = on_connect
client.connect(BROKER, PORT, 10)
client.loop_start()


while end_time is None:
    time.sleep(0.1)

end_dt = end_time

# print(f"T0: {start_dt.strftime('%Y-%m-%d %H:%M:%S.%f')}")
# # 4. Imprimir el tiempo final y la diferencia
# print(f"T1: {end_dt.strftime('%Y-%m-%d %H:%M:%S.%f')}")

elapsed_time = end_time - start_time
# print(f"L: {elapsed_time*1000:.4f} milisegundos")
time.sleep(5)  # Esperar un poco para asegurarnos de que el cliente se desconecte correctamente
print(f"{start_dt}, {end_dt}, {elapsed_time:.4f}")

while True:
    time.sleep(1)
