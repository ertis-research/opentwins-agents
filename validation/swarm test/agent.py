import json
import os
import random
import time

import numpy as np
import paho.mqtt.client as mqtt


BROKER = os.getenv("MQTT_BROKER", "<MQTT_BROKER_HOST>")
PORT = int(os.getenv("MQTT_PORT", 1883))

AGENT_ID = os.getenv("AGENT_ID", f"agent-{random.randint(0,9999)}")

UPDATE_INTERVAL = 0.1
NEIGHBOR_RADIUS = 50.0
MAX_SPEED = 2.0
LOSS_RATE = 0.05


# NUEVO: Definimos el tamaño del mundo para que la matemática funcione
WORLD_SIZE = 50.0 

class SwarmAgent:

    def __init__(self):
        self.position = np.random.rand(3) * WORLD_SIZE
        self.velocity = (np.random.rand(3) - 0.5)

        self.neighbors = {}

        self.client = mqtt.Client(
            client_id=AGENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.client.username_pw_set("<MQTT_USER>", "<MQTT_PASSWORD>")
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT)
        self.client.subscribe("test/gedera/swarm/agents/+/state")
        self.client.loop_start()

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            if payload["id"] == AGENT_ID:
                return
            self.neighbors[payload["id"]] = payload
        except Exception as e:
            pass

    # ---------------- MATEMÁTICA TOROIDAL ----------------
    
    def _get_toroidal_diff(self, target_pos):
        """
        Calcula el vector más corto desde mí hacia el objetivo, 
        cruzando los bordes del mapa si es necesario.
        """
        diff = target_pos - self.position
        # Fórmula de frontera periódica (envuelve los valores al camino más corto)
        diff = diff - WORLD_SIZE * np.round(diff / WORLD_SIZE)
        return diff

    # ---------------- COMPORTAMIENTO ----------------

    def separation(self):
        force = np.zeros(3)

        for neighbor in self.neighbors.values():
            pos = np.array(neighbor["position"])
            
            # Usamos la diferencia toroidal en lugar de la resta normal
            diff = self._get_toroidal_diff(pos)
            distance = np.linalg.norm(diff)

            if 0 < distance < 1.5:
                # Nos alejamos en dirección contraria al objetivo
                force -= diff / (distance + 1e-6)

        return force

    def cohesion(self):
        valid_diffs = []

        for neighbor in self.neighbors.values():
            pos = np.array(neighbor["position"])
            
            diff = self._get_toroidal_diff(pos)
            distance = np.linalg.norm(diff)

            if distance < NEIGHBOR_RADIUS:
                # En un toroide NO se pueden hacer medias de posiciones absolutas (49 + 1)/2 = 25 (¡falso!).
                # Se hacen medias de los "vectores direccionales" (diff).
                valid_diffs.append(diff)

        if not valid_diffs:
            return np.zeros(3)

        # Hacia dónde está el centroide de mis vecinos relativo a mi posición actual
        avg_diff = np.mean(valid_diffs, axis=0)
        return avg_diff * 0.01

    def alignment(self):
        valid_velocities = []

        for neighbor in self.neighbors.values():
            pos = np.array(neighbor["position"])
            
            # Solo consideramos la distancia toroidal para saber si está en el radio
            diff = self._get_toroidal_diff(pos)
            distance = np.linalg.norm(diff)

            if distance < NEIGHBOR_RADIUS:
                valid_velocities.append(np.array(neighbor["velocity"]))

        if not valid_velocities:
            return np.zeros(3)

        avg_velocity = np.mean(valid_velocities, axis=0)
        return (avg_velocity - self.velocity) * 0.05

    def update(self):
        sep = self.separation() * 1.5
        coh = self.cohesion() * 1.0
        ali = self.alignment() * 1.0

        acceleration = sep + coh + ali
        noise = np.random.normal(0, 0.02, 3)

        self.velocity += acceleration + noise

        speed = np.linalg.norm(self.velocity)
        if speed > MAX_SPEED:
            self.velocity = self.velocity / speed * MAX_SPEED

        self.position += self.velocity * UPDATE_INTERVAL

        # NUEVO: Efecto Pac-Man. Si el dron cruza 50, vuelve por el 0.
        self.position = self.position % WORLD_SIZE

    def publish_state(self):
        if random.random() < LOSS_RATE:
            return

        payload = {
            "id": AGENT_ID,
            "timestamp": time.time(),
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist()
        }

        self.client.publish(
            f"test/gedera/swarm/agents/{AGENT_ID}/state",
            json.dumps(payload),
            qos=0
        )

    def run(self):
        while True:
            self.update()
            self.publish_state()
            print(f"[{AGENT_ID}] pos={self.position.round(1)} vel={self.velocity.round(2)}")
            time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    agent = SwarmAgent()
    agent.run()