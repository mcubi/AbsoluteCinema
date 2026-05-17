from __future__ import annotations

import os
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import UserProfile

# Google libraries (already used elsewhere in your project)
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'status': 'error', 'error': message}, status=status)


@csrf_exempt
def _parse_json_body(request: HttpRequest) -> dict:
    """
    Parser tolerante para recibir JSON desde distintos clientes (curl/navegador/Windows).
    Soporta:
    - UTF-8 BOM
    - casos raros donde el body llega “escapado” (backslashes extra)
    """
    raw = request.body.decode('utf-8-sig', errors='ignore').strip()
    if not raw:
        return {}

    # 1) intento normal
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2) si parece que llega escapado, intentamos desescapar
    # Ejemplo problemático visto: "{\\ username\\:\\ ... }"
    try:
        candidate = raw
        if candidate.startswith('{') and '\\' in candidate:
            candidate = candidate.replace('\\', '')
        return json.loads(candidate)
    except Exception:
        pass

    # 3) último intento: unicode escape (solo si parece que viene “escapado”)
    try:
        seems_escaped = ('\\\\' in raw) or ('\\u' in raw) or ('\\"' in raw)
        if seems_escaped:
            candidate = raw.encode('utf-8').decode('unicode_escape')
            return json.loads(candidate)
    except Exception:
        pass

    # si nada funciona, propagamos error original
    return json.loads(raw)


@csrf_exempt
def api_register(request: HttpRequest) -> JsonResponse:
    """API para registro.

    POST body JSON:
      {
        "username": "...",
        "password": "...",
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "telefono": "..."
      }

    - Crea User (Django auth)
    - Crea UserProfile asociado
    """

    if request.method != 'POST':
        return _json_error('Método no permitido', status=405)

    try:
        payload = _parse_json_body(request)
    except Exception as e:
        sample = request.body[:200]
        return _json_error(f'JSON inválido ({e}); body={sample!r}')

    required = ['username', 'password', 'first_name', 'last_name', 'email', 'telefono']
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return _json_error(f'Faltan campos: {", ".join(missing)}')

    username = payload['username']
    email = payload['email']

    if User.objects.filter(username=username).exists():
        return _json_error('Este username ya existe')

    if UserProfile.objects.filter(email=email).exists():
        return _json_error('Este email ya está registrado')

    user = User.objects.create_user(
        username=username,
        password=payload['password'],
        email=email,
        first_name=payload['first_name'],
        last_name=payload['last_name'],
    )

    # UserProfile: unique constraint en email/telefono
    UserProfile.objects.create(
        user=user,
        first_name=payload['first_name'],
        last_name=payload['last_name'],
        email=email,
        telefono=payload['telefono'],
    )

    return JsonResponse({'status': 'success', 'message': 'Usuario registrado'})


@csrf_exempt
def api_login(request: HttpRequest) -> JsonResponse:
    """API para login.

    POST body JSON:
      {"username": "...", "password": "..."}

    - authenticate() con Django auth
    - login() para iniciar sesión en la cookie de sesión
    """

    if request.method != 'POST':
        return _json_error('Método no permitido', status=405)

    try:
        payload = _parse_json_body(request)
    except Exception as e:
        sample = request.body[:200]
        return _json_error(f'JSON inválido ({e}); body={sample!r}')

    username = payload.get('username')
    password = payload.get('password')

    if not username or not password:
        return _json_error('username y password son obligatorios')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return _json_error('Credenciales inválidas', status=401)

    login(request, user)
    return JsonResponse({'status': 'success', 'message': 'Login correcto'})


@login_required
@csrf_exempt
def api_logout(request: HttpRequest) -> JsonResponse:
    """API logout."""
    if request.method != 'POST':
        return _json_error('Método no permitido', status=405)

    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Logout correcto'})


@csrf_exempt
def api_google_auth(request: HttpRequest) -> JsonResponse:
    """API para login con Google (token ID).

    POST body JSON:
      {"credential": "<id token>"}

    - Verifica el token con GOOGLE_CLIENT_ID (desde .env)
    - Busca/crea User + UserProfile por email
    - Hace login(request, user)
    """

    if request.method != 'POST':
        return _json_error('Método no permitido', status=405)

    try:
        payload = _parse_json_body(request)
    except Exception as e:
        sample = request.body[:200]
        return _json_error(f'JSON inválido ({e}); body={sample!r}')

    credential = payload.get('credential')
    if not credential:
        return _json_error('No se proporcionó el token de credencial', status=400)

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    if not client_id:
        return _json_error('Falta GOOGLE_CLIENT_ID en .env', status=500)

    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as e:
        return _json_error(f'Token de Google inválido: {e}', status=401)

    email = id_info.get('email')
    if not email:
        return _json_error('El token no trae email', status=400)

    first_name = id_info.get('given_name', '')
    last_name = id_info.get('family_name', '')

    username_base = email.split('@')[0]

    # Buscar por email
    user = User.objects.filter(email=email).first()

    if user is None:
        # Asegura username único
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            telefono='',  # si tu modelo exige teléfono real, luego lo ajustamos
        )

    login(request, user)
    return JsonResponse({'status': 'success', 'message': 'Google login correcto'})

