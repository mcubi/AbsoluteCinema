# IMPORTS
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile # noqa
from .forms import RegistroForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import LoginForm

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
                
                # El signal ya ha creado el perfil. Ahora, si el usuario introdujo un teléfono, lo guardamos.
                if telefono:
                    user.perfil.telefono = telefono
                    user.perfil.save()

                messages.success(request, "Usuario registrado correctamente")
                return redirect('users:log_in')

            except Exception as e:
                messages.error(request, f"Error al registrar: {e}")

        
        return render(request, 'users/register.html', {'form': form})

    else:
        form = RegistroForm()

    return render(request, 'users/register.html', {'form': form})

# ***********************************************************************************+

# LOG IN

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = LoginForm()
        
    return render(request, 'users/login.html', {'form': form})

# ***********************************************************************************+

# LOG OUT

@login_required
def user_logout(request):
    
    # Close sesion
    logout(request)
    
    messages.success(request, "Cerraste la sesión con anterioridad")
    return redirect('home')  # Redirige a la página principal

# ***********************************************************************************+

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
    user = request.user
    
    if request.method == 'POST':
        # Recoger datos del formulario manual
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        avatar = request.FILES.get('avatar')
        
        # Actualizar usuario (esto cambia el nombre que aparece en el @)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Actualizar perfil
        perfil.telefono = telefono
        if avatar:
            perfil.avatar = avatar
        perfil.save()
        
        messages.success(request, "Perfil actualizado correctamente")
        return redirect('users:configuracion')
    
    return render(request, 'users/configuracion.html', {
        'perfil': perfil,
        'user': user,
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
    
    messages.error(request, 'Tu cuenta ha sido eliminada permanentemente.')
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