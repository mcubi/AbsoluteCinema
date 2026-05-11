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

    return render(request, 'users/register.html', {'form': form})

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
            
    return render(request, 'users/login.html')

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