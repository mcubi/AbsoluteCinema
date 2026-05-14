#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absolute_cinema.settings')

import django
django.setup()

# Importar y ejecutar Daphne
from daphne.endpoints import build_endpoint_description_strings
from daphne.server import Server
from daphne.http_protocol import HTTPFactory
from daphne.ws_protocol import WebSocketFactory
from daphne.autobahn import AutobahnWebSocketFactory

from django.core.asgi import get_asgi_application

application = get_asgi_application()

# Configurar el servidor
server = Server(
    application=application,
    endpoints=build_endpoint_description_strings(host="0.0.0.0", port=8001),
    verbosity=1,
    access_log="-",
)

print("Iniciando servidor ASGI en http://127.0.0.1:8001/")
server.run()
