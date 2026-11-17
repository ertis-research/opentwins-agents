# Usamos una versión oficial y ligera de Python
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza a que los prints salgan directos al log (muy útil en K8s)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos y establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero SOLO el requirements (esto optimiza la caché de Docker)


# Instalamos las librerías
RUN pip install --no-cache-dir numpy==1.26.4
RUN pip install --no-cache-dir paho-mqtt==2.0.0
RUN pip install --no-cache-dir pandas==2.0.3

# Ahora copiamos el resto de nuestro código (el agent.py)
COPY . .

# Comando por defecto al arrancar el contenedor
CMD ["python", "agent.py"]