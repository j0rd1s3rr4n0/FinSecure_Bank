# Usa una imagen oficial de Python
FROM python:3.14.0rc1-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos locales al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto para ejecutar la app
EXPOSE 80
CMD ["python", "run.py"]
