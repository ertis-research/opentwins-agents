# Utilizamos una imagen oficial y ligera de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos la librería paho-mqtt
# (Si tuvieras más dependencias, lo ideal sería usar un requirements.txt)
RUN pip install --no-cache-dir paho-mqtt

# Copiamos nuestro script al directorio de trabajo del contenedor
COPY ready.py .
ENV PYTHONUNBUFFERED=1
# Comando que se ejecutará al iniciar el contenedor
CMD ["python", "ready.py"]