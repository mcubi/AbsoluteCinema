FROM python:3-slim

WORKDIR /app

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app

#Crea un usuario sin privilegios
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# En lugar de ENTRYPOINT, usa CMD (no necesita entrypoint.sh)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]