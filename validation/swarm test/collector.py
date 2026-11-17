import json
import os
import time
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt


BROKER = os.getenv("MQTT_BROKER", "<MQTT_BROKER_HOST>")
PORT = int(os.getenv("MQTT_PORT", 1883))

MIN_AGENTS_READY = 20 # Cambia esto según el tamaño de tu test
WORLD_SIZE = 50.0

history = []

class SwarmCollector:

    def __init__(self):
        self.states = {}

        # Historial (ventana temporal) para la máquina de estados
        self.alignment_history = []
        self.cohesion_history = []
        self.distance_history = []

        self.window = 20

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.client.username_pw_set("<MQTT_USER>", "<MQTT_PASSWORD>")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER, PORT)
        self.client.subscribe("test/gedera/swarm/agents/+/state")
        self.client.loop_start()

    # ---------------- MQTT callbacks ----------------

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        print(f"[collector] MQTT conectado: {reason_code}")

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            self.states[payload["id"]] = payload
        except Exception as e:
            pass # Ignoramos errores de parseo silenciándolos

    # ---------------- METRICAS TOROIDALES ----------------

    def _positions(self):
        return np.array([s["position"] for s in self.states.values()])

    def _velocities(self):
        return np.array([s["velocity"] for s in self.states.values()])

    def _toroidal_diff(self, p1, p2):
        """Calcula el vector de distancia más corto en un toroide (Efecto Pac-Man)."""
        diff = p1 - p2
        return diff - WORLD_SIZE * np.round(diff / WORLD_SIZE)

    def _toroidal_centroid(self, pos):
        """Calcula el verdadero centro de masa en un mundo cerrado usando trigonometría."""
        # Convertimos las coordenadas a radianes (0 a 2*PI)
        angles = (pos / WORLD_SIZE) * 2 * np.pi
        
        # Calculamos la media del seno y el coseno
        mean_cos = np.mean(np.cos(angles), axis=0)
        mean_sin = np.mean(np.sin(angles), axis=0)
        
        # Recuperamos el ángulo promedio y lo pasamos de nuevo a coordenadas del mundo
        mean_angle = np.arctan2(mean_sin, mean_cos)
        centroid = (mean_angle / (2 * np.pi)) * WORLD_SIZE
        
        return np.mod(centroid, WORLD_SIZE)

    def order_parameter(self):
        """Mide qué tan alineadas están las velocidades (0 = caos, 1 = perfecta sincronía)."""
        v = self._velocities()
        if len(v) == 0: 
            return 0.0
            
        norms = np.linalg.norm(v, axis=1) + 1e-9
        v_norm = v / norms[:, None]
        mean_vector = np.mean(v_norm, axis=0)
        return np.linalg.norm(mean_vector)

    def cohesion_metric(self):
        """Mide la distancia promedio de los agentes al centroide toroidal."""
        pos = self._positions()
        if len(pos) < 2: 
            return 0.0
        
        centroid = self._toroidal_centroid(pos)
        
        # Calculamos la distancia toroidal real de cada dron a ese centroide
        diffs = np.array([self._toroidal_diff(p, centroid) for p in pos])
        dist = np.linalg.norm(diffs, axis=1)
        
        return float(np.mean(dist))

    def min_distance(self):
        """Detecta la distancia entre los dos drones más cercanos (para evitar colisiones)."""
        pos = self._positions()
        if len(pos) < 2: 
            return 0.0
            
        min_d = float("inf")
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                d = np.linalg.norm(self._toroidal_diff(pos[i], pos[j]))
                min_d = min(min_d, d)
                
        return min_d if min_d != float("inf") else 0.0

    def isolated_agents(self, threshold=3.0):
        """Cuenta cuántos agentes no tienen a ningún vecino en su radio visual."""
        pos = self._positions()
        isolated_count = 0
        
        for i in range(len(pos)):
            has_neighbor = False
            for j in range(len(pos)):
                if i == j:
                    continue
                if np.linalg.norm(self._toroidal_diff(pos[i], pos[j])) < threshold:
                    has_neighbor = True
                    break
            if not has_neighbor:
                isolated_count += 1
                
        return isolated_count

    # ---------------- CLASIFICADOR DE ESTADOS ----------------

    def classify_state(self):
        """Máquina de estados finita basada en las matemáticas del enjambre."""
        if len(self.alignment_history) < self.window:
            return "WARMUP"

        a_mean = np.mean(self.alignment_history)
        c_mean = np.mean(self.cohesion_history)

        if a_mean < 0.6:
            return "DISORDERED"
        elif a_mean >= 0.85:
            # Tolerancia de cohesión ajustada al tamaño del toroide
            if c_mean < 2.5: 
                return "COHERENT_MOTION"
            else:
                return "SWARM_EXPANDED"
        else:
            return "TRANSITION"

    # ---------------- BUCLE PRINCIPAL ----------------

    def print_metrics(self):
        n_agents = len(self.states)

        # GUARD: No se hace nada hasta que el enjambre mínimo esté conectado
        if n_agents < MIN_AGENTS_READY:
            print(f"Waiting for agents... ({n_agents}/{MIN_AGENTS_READY})")
            return

        alignment = self.order_parameter()
        cohesion = self.cohesion_metric()
        min_d = self.min_distance()
        isolated = self.isolated_agents()

        self.alignment_history.append(alignment)
        self.cohesion_history.append(cohesion)
        self.distance_history.append(min_d)

        # Mantener la ventana temporal de tamaño fijo
        if len(self.alignment_history) > self.window:
            self.alignment_history.pop(0)
            self.cohesion_history.pop(0)
            self.distance_history.pop(0)

        state = self.classify_state()

        print("=" * 60)
        print(f"agents         : {n_agents}")
        print(f"order_param    : {alignment:.3f}")
        print(f"cohesion       : {cohesion:.3f}")
        print(f"min_distance   : {min_d:.3f}")
        print(f"isolated_agents: {isolated}")
        print(f"state          : {state}")
        
        
        history.append({
            "agents": n_agents,
            "order_param": alignment,
            "cohesion": cohesion,
            "min_distance": min_d,
            "isolated_agents": isolated,
            "state": state
        })
        
    def save_to_csv(self):
        if not history:
            print("\n[collector] No hay datos guardados para exportar.")
            return
            
        df = pd.DataFrame(history)
        filename = f"swarm_metrics_{int(time.time())}.csv"
        df.to_csv(filename, index=False)
            
        print(f"\n[collector] ¡Métricas exportadas correctamente a {filename}!")

    def run(self):
        print("[collector] Iniciando recolección. Pulsa Ctrl+C para guardar y salir.")
        try:
            while True:
                self.print_metrics()
                time.sleep(2)
        except KeyboardInterrupt:
            # Capturamos cuando el usuario hace Ctrl+C
            print("\n[collector] Interrupción detectada. Preparando datos...")
            self.save_to_csv()
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    collector = SwarmCollector()
    collector.run()