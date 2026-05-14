#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absolute_cinema.settings')

# Importar Django
import django
django.setup()

# Importar y ejecutar Daphne
import subprocess

# Ejecutar Daphne con las variables de entorno correctas
cmd = [
    sys.executable, '-m', 'daphne',
    '-b', '127.0.0.1',
    '-p', '8001',
    'absolute_cinema.asgi:application',
    '--access-log', '-'
]

print("Iniciando servidor ASGI con Daphne...")
print("Servidor disponible en: http://127.0.0.1:8001/")
print("WebSocket URL: ws://127.0.0.1:8001/ws/reviews/<movie_id>/")

subprocess.run(cmd, env=os.environ.copy())
