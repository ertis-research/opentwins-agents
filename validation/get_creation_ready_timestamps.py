import subprocess
import pandas as pd

# Namespace donde están los pods
NAMESPACE = "opentwins"

# CSV de salida

def get_pod_timestamps(timestamp, grupo):
    OUTPUT_CSV = f"datasets_deploy/pod_receptor_ready_times_{grupo}.csv"
    # 1️⃣ Obtener todos los pods que contengan 'receptor' en su nombre
    get_pods_cmd = [
        "kubectl", "get", "pods",
        "-n", NAMESPACE,
        "-o", "name"
    ]

    pods_output = subprocess.check_output(get_pods_cmd, text=True).splitlines()
    # Filtrar solo los que contienen 'receptor'
    pods = []
    for p in pods_output:
        if "emisor" in p:
            pods.append(p.split("/")[1])
        elif "receptor" in p:
            pods.append(p.split("/")[1])
    print(f"Found pods: {pods}")

    # 2️⃣ Extraer timestamps de cada pod
    data = []

    for pod in pods:
        # creationTimestamp
        creation_cmd = [
            "kubectl", "get", "pod", pod,
            "-n", NAMESPACE,
            "-o", "jsonpath={.metadata.creationTimestamp}"
        ]
        creation_ts = subprocess.check_output(creation_cmd, text=True).strip()

        # Ready lastTransitionTime
        ready_cmd = [
            "kubectl", "get", "pod", pod,
            "-n", NAMESPACE,
            "-o", "jsonpath={.status.conditions[?(@.type=='Ready')].lastTransitionTime}"
        ]
        ready_ts = subprocess.check_output(ready_cmd, text=True).strip()

        data.append({
            "grupo": grupo,
            "apiTimestamp": timestamp,
            "nombre": pod.split("-")[2]+"-"+pod.split("-")[3],
            "creationTimestamp": creation_ts,
            "readyTimestamp": ready_ts
        })

    # 3️⃣ Guardar en CSV
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Dataset generado en {OUTPUT_CSV}")