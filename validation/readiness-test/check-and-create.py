#!/usr/bin/env python3

"""
Script para medir:
- creationTimestamp (K8s)
- Ready time (K8s)
- container start (K8s)
- MQTT connect (log interno con timestamps)

El script:
1. Detecta pod actual
2. Lo elimina
3. Espera nuevo pod
4. Captura timestamps reales de K8s
5. Lee primer log estructurado
6. Calcula métricas
7. Repite

Requisitos:
- kubectl configurado
- relojes sincronizados (NTP)
- logs con formato: <ts_start> <ts_mqtt> <latencia>
"""

import subprocess
import time
import json
import re
import csv
from datetime import datetime

NAMESPACE = "gedera-test"
LABEL_SELECTOR = "app=mqtt-timer-pod"
RUNS = 30
OUTPUT = "results.csv"
POLL = 2

LOG_REGEX = re.compile(r"(\d+)\s+(\d+)\s+([0-9.]+)")


def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)


def get_pods():
    data = sh(f"kubectl get pods -n {NAMESPACE} -l {LABEL_SELECTOR} -o json")
    return json.loads(data)["items"]


def get_pod(name):
    data = sh(f"kubectl get pod {name} -n {NAMESPACE} -o json")
    return json.loads(data)


def delete_pod(name):
    subprocess.call(f"kubectl delete pod {name} -n {NAMESPACE} --grace-period=0 --force", shell=True)


def wait_new_pod(old_name):
    while True:
        pods = get_pods()
        for p in pods:
            name = p["metadata"]["name"]
            if name != old_name:
                return name
        time.sleep(POLL)


def get_creation_ts(pod):
    return pod["metadata"]["creationTimestamp"]


def get_ready_ts(pod):
    for c in pod["status"].get("conditions", []):
        if c["type"] == "Ready" and c["status"] == "True":
            return c["lastTransitionTime"]
    return None


def get_started_ts(pod):
    try:
        return pod["status"]["containerStatuses"][0]["state"]["running"]["startedAt"]
    except Exception:
        return None


def wait_ready_and_started(pod_name):
    t_ready = None
    t_started = None

    while True:
        pod = get_pod(pod_name)

        if not t_started:
            t_started = get_started_ts(pod)

        if not t_ready:
            t_ready = get_ready_ts(pod)

        if t_ready and t_started:
            return t_started, t_ready

        time.sleep(POLL)


def wait_mqtt_log(pod_name):
    seen = set()

    while True:
        logs = sh(f"kubectl logs {pod_name} -n {NAMESPACE} --tail=50")

        for line in logs.splitlines():
            if line in seen:
                continue
            seen.add(line)
            
            m = line.split(", ")
            return m[0], m[1], float(m[2])


        time.sleep(0.2)


def iso_to_ms(ts):
    # convierte RFC3339 a ms
    from datetime import datetime
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def run_once(i):
    print(f"Run {i}")

    pods = get_pods()
    if not pods:
        raise RuntimeError("No hay pods")

    old = pods[0]["metadata"]["name"]
    
    print("Eliminando pod actual:", old)

    delete_pod(old)
    
    print("Esperando nuevo pod...")

    new = wait_new_pod(old)

    print("Nuevo pod detectado:", new)
    
    pod = get_pod(new)
    
    print("Esperando Ready y Started...")
    t_create = iso_to_ms(get_creation_ts(pod))

    t_started_iso, t_ready_iso = wait_ready_and_started(new)

    t_started = iso_to_ms(t_started_iso)
    t_ready = iso_to_ms(t_ready_iso)

    ts_app_start, ts_mqtt, latency = wait_mqtt_log(new)
    print(f"Log MQTT: app_start={ts_app_start}, mqtt={ts_mqtt}, latency={latency} ms")
    return {
        "run": i,
        "t_create": t_create,
        "t_started": t_started,
        "t_ready": t_ready,
        "ts_app_start": ts_app_start,
        "ts_mqtt": ts_mqtt,
        "latency": latency
    }


def compute(row):
    
    return {
        "run": row["run"],
        "ready_time": row["t_ready"] - row["t_create"],
        "startup_time": row["t_started"] - row["t_create"],
        "mqtt_after_start": row["ts_mqtt"] - row["t_started"],
        "total_recovery": row["ts_mqtt"] - row["t_create"],
        "app_latency": row["latency"]
    }


def main():
    raw = []
    results = []

    for i in range(RUNS):
        row = run_once(i)
        results.append(row)
        # results.append(compute(row))
        print(results[-1])

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
