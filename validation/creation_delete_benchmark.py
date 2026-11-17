from deploy import *
from get_creation_ready_timestamps import *
import subprocess
import time
# Sustituye esta URL por la de tu API real de Kubernetes
URL_DESTINO = "<AGENTS_API_URL>"

# Llamamos a la función

def deployment_ready(deployment_name, namespace="default"):
    """
    Devuelve True si todos los pods del deployment están Ready, False en caso contrario.
    """
    try:
        pods = subprocess.check_output(
            ["kubectl", "get", "pods", "-n", namespace, "-l", f"app={deployment_name}", "-o", "name"],
            text=True
        ).splitlines()
        
        for p in pods:
            ready = subprocess.check_output(
                ["kubectl", "get", p, "-n", namespace, "-o",
                 "jsonpath={.status.conditions[?(@.type=='Ready')].status}"],
                text=True
            ).strip()
            if ready != "True":
                return False
        return True
    except subprocess.CalledProcessError:
        return False
    
def deployments_ready(number_deployments):
    for i in range(1, number_deployments+1):
        if not deployment_ready(f"emisor-app-{i}", namespace="opentwins"):
            return False
    return True

def pod_exists(substring, namespace="default"):
    """
    Devuelve True si hay al menos un pod cuyo nombre contenga 'substring'.
    """
    try:
        pods = subprocess.check_output(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "name"],
            text=True
        ).splitlines()
        
        # Filtramos por el substring en el nombre del pod
        for p in pods:
            pod_name = p.split("/")[1]  # 'pod/<nombre>'
            if substring in pod_name:
                return True
        return False
    except subprocess.CalledProcessError:
        return False

def delete_deployments(group, namespace):
    for i in range(1, group+1):
        subprocess.run(f"kubectl delete deployment opentwins-agent-emisor-{i} -n {namespace}", shell=True)
        subprocess.run(f"kubectl delete deployment opentwins-agent-receptor-{i} -n {namespace}", shell=True)

for i in range(62, 101):
    print("Deploying group ", i)
    timestamp = desplegar_flota(URL_DESTINO, total_nodos=i)
    
    while not deployments_ready(i):
        time.sleep(1)
        
    print("All deployments in group ", i, " are ready. Gathering timestamps...")
    get_pod_timestamps(timestamp, i)
    
    time.sleep(2)
    
    print("Cleaning up group ", i)
    delete_deployments(i, "opentwins")
    
    print("All deployments in group ", i, " deleted. Waiting for pods to terminate...")
    while pod_exists("receptor", namespace="opentwins"):
        time.sleep(1)
    while pod_exists("emisor", namespace="opentwins"):
        time.sleep(1)
        
    
    

    