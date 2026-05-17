# IMPORTS
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistroForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# ***********************************************************************************+
                                        # VIEWS
# ***********************************************************************************+  

# REGISTER

def register_user(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            try:
                
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                telefono = form.cleaned_data['telefono']

             
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )

                
                profile = UserProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    telefono=telefono
                )

                messages.success(request, "Usuario registrado correctamente")
                return redirect('users:log_in')

            except Exception as e:
                messages.error(request, f"Error al registrar: {e}")

        
        return render(request, 'users/register.html', {'form': form})

    else:
        form = RegistroForm()

    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render(request, 'users/register.html', {'form': form, 'GOOGLE_CLIENT_ID': google_client_id})


# ***********************************************************************************+

# LOG IN

def login_user(request):
    if request.method == 'POST':
        # Pillamos los datos que envía el formulario HTML
        usuario = request.POST.get('username')
        contra = request.POST.get('password')

        # Django comprueba si existe y la contraseña es correcta
        user = authenticate(request, username=usuario, password=contra)

        if user is not None:
            # Si está todo OK, iniciamos la sesión
            login(request, user)
            # Y lo mandamos a la página principal (home)
            return redirect('home')
        else:
            # Si falla, mandamos un mensaje de error
            messages.error(request, "Usuario o contraseña incorrectos")

    # Para que login.html tenga el clientId del OAuth client correcto
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render(request, 'users/login.html', {'GOOGLE_CLIENT_ID': google_client_id})

# ***********************************************************************************+

# LOG OUT

@login_required
def user_logout(request):
    
    # Close sesion
    logout(request)
    
    messages.success(request, "Cerraste la sesión con anterioridad")
    return redirect('home')  # Redirige a la página principal

# ***********************************************************************************+

# GOOGLE AUTH

@csrf_exempt
def google_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        credential = data.get('credential')

        if not credential:
            return JsonResponse({'error': 'No se ha proporcionado el token de credencial'}, status=400)

        # client_id debe ser EL MISMO que el clientId del frontend.
        # (Recomendado: tenerlo en .env)
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not client_id:
            return JsonResponse({'error': 'Falta GOOGLE_CLIENT_ID en .env'}, status=500)


        # Verificar el token con los servidores de Google
        id_info = id_token.verify_oauth2_token(credential, google_requests.Request(), client_id)

        email = id_info.get('email')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        
        # Generar un nombre de usuario único a partir del email
        username = email.split('@')[0]

        # Intentar encontrar al usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Si no existe, lo creamos
            # Nos aseguramos de que el username sea único
            temp_username = username
            counter = 1
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{username}{counter}"
                counter += 1
            username = temp_username

            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
            # Creamos el perfil de usuario asociado
            UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)

        # Iniciar sesión con el usuario
        login(request, user)

        return JsonResponse({'status': 'success', 'message': 'Inicio de sesión con Google correcto'})

    except ValueError as e:
        # El token no es válido
        return JsonResponse({'error': f'Token de Google inválido: {e}'}, status=401)
    except Exception as e:
        return JsonResponse({'error': f'Ha ocurrido un error inesperado: {e}'}, status=500)

# USER PROFILE

from django.contrib.auth.decorators import login_required

@login_required
def mi_perfil(request):
    perfil = request.user.perfil
    return render(request, 'users/mi_perfil.html', {'perfil': perfil})

# ***********************************************************************************+

# CONFIG PROFILE


@login_required
def configuracion(request):
    # get the actual user's profile
    perfil = request.user.perfil
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('users:configuracion')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'users/configuracion.html', {
        'form': form,
        'perfil': perfil,
    })

# ***********************************************************************************+

# DELETING ACCOUNTS

@login_required
def delete_account(request):
    user = request.user
    
    # Password verify
    password = request.POST.get('password')
    if not user.check_password(password):
        messages.error(request, 'Contraseña incorrecta. No se pudo eliminar la cuenta.')
        return redirect('users:configuracion')
    
    # Avatar existance checking and deletion
    try:
        if hasattr(user, 'perfil') and user.perfil.avatar:
            avatar_path = user.perfil.avatar.path
            if os.path.isfile(avatar_path):
                os.remove(avatar_path)
    except Exception as e:
        print(f"Error al eliminar avatar: {e}")
    
    # Close session
    logout(request)
    
    # Delete user ==== PROFILE will be destroyed too cause of CASCADE condition in PROFILE MODEL
    user.delete()
    
    messages.success(request, 'Tu cuenta ha sido eliminada permanentemente.')
    return redirect('home')

# **************************************************************************************************+

# CHANGE PASSWORD

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión para que no cierre sesión
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('users:configuracion')
        
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})