import os
import shutil

# Carpeta de origen (donde están las subcarpetas de cada pod)
backup_dir = "backup"

# Carpeta de destino (donde se guardarán los archivos más pesados)
datasets_dir = "datasets"
os.makedirs(datasets_dir, exist_ok=True)

# Recorremos cada subcarpeta
for pod_folder in os.listdir(backup_dir):
    pod_path = os.path.join(backup_dir, pod_folder)
    
    # Asegurarnos de que es una carpeta
    if not os.path.isdir(pod_path):
        continue

    # Listar solo archivos (ignorar subcarpetas)
    files = [f for f in os.listdir(pod_path) if os.path.isfile(os.path.join(pod_path, f))]
    
    if not files:
        print(f"No hay archivos en {pod_folder}")
        continue
    
    # Encontrar el archivo más pesado
    heaviest_file = max(files, key=lambda f: os.path.getsize(os.path.join(pod_path, f)))
    source_file = os.path.join(pod_path, heaviest_file)
    
    # Copiar al folder datasets, manteniendo el nombre del pod para no sobrescribir
    dest_file = os.path.join(datasets_dir, f"{pod_folder}_{heaviest_file}")
    shutil.copy2(source_file, dest_file)
    
    print(f"Copiado {heaviest_file} de {pod_folder} -> {dest_file}")