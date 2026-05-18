FROM python:3-slim

WORKDIR /app

EXPOSE 8000

# Impide que Python genere archivos en .pyc del contenedor
ENV PYTHONDONTWRITEBYTECODE=1

# desactiva el almacenamiento en el buffer para facilitar el registro de contenedores
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala pip requirements con cuidado y sutileza
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app

#Crea un usuario sin privilegios de administrador con un uid explícito y le otorga permiso para acceder a la carpeta de la app
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]