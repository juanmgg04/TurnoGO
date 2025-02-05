# Usa una imagen base de Python
FROM python:3.12

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app
COPY requirements.txt .

# Instalar las dependencias
RUN pip install -r requirements.txt