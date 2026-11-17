import requests
import time
from datetime import datetime

def enviar_manifiesto_json(url_endpoint, payload_json, tipo, numero):
    """
    Función auxiliar para enviar el diccionario como JSON y gestionar los errores.
    """
    print(f"[*] Desplegando {tipo} #{numero}...")
    try:
        # Al usar json=payload_json, requests convierte el diccionario a JSON 
        # y añade automáticamente la cabecera 'Content-Type: application/json'
        respuesta = requests.post(url_endpoint+"/"+tipo.lower()+f"-{numero}", json=payload_json)
        respuesta.raise_for_status() 
        print(f"  [+] Éxito: {tipo}-{numero} creado.")
        
    except requests.exceptions.RequestException as e:
        print(f"  [-] Error al desplegar {tipo}-{numero}: {e}")
        # Intentamos imprimir el mensaje de error del servidor si existe
        if 'respuesta' in locals() and respuesta is not None:
            print(f"      Detalle del servidor: {respuesta.text}")


def desplegar_flota(url_endpoint, total_nodos=100):
    """
    Genera y envía los manifiestos JSON para N emisores y N receptores.
    """
    
    timestamp = datetime.now().isoformat()  # Timestamp para el dataset
    for i in range(1, total_nodos + 1):

        # ---------------------------------------------------------
        # 1. DICCIONARIO PARA EL EMISOR
        # ---------------------------------------------------------
        json_emisor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"emisor-app-{i}",  
                "labels": {
                    "opentwins.agents/name": f"emisor-{i}",
                    "opentwins.agents/twins": []
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": f"emisor-{i}"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"emisor-{i}"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "emisor-container",
                                "image": "<DOCKER_REGISTRY>/gedera/emisor:1.0.0",
                                "imagePullPolicy": "Always",
                                "env": [
                                    {
                                        "name": "NAME",
                                        "value": str(i) # Convertimos el número a string explícitamente
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        enviar_manifiesto_json(url_endpoint, json_emisor, "Emisor", i)
        
        # ---------------------------------------------------------
        # 2. DICCIONARIO PARA EL RECEPTOR
        # ---------------------------------------------------------
        json_receptor = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"receptor-app-{i}",  
                "labels": {
                    "opentwins.agents/name": f"receptor-{i}",
                    "opentwins.agents/twins": []
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": f"receptor-{i}"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"receptor-{i}"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "receptor-container",
                                "image": "<DOCKER_REGISTRY>/gedera/receptor:1.0.0",
                                "imagePullPolicy": "Always",
                                "env": [
                                    {
                                        "name": "NAME",
                                        "value": str(i)
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        enviar_manifiesto_json(url_endpoint, json_receptor, "Receptor", i)
        
        # Pequeña pausa de 100ms para no saturar la API
        time.sleep(0.1) 

    print("\n[✓] Proceso de despliegue masivo finalizado.")
    
    return timestamp  # Devolvemos el timestamp para usarlo en el dataset de timestamps

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # Sustituye esta URL por la de tu API real de Kubernetes
    URL_DESTINO = "<AGENTS_API_URL>"
    
    # Llamamos a la función
    desplegar_flota(URL_DESTINO, total_nodos=100)
    
    
    
    
