# IMPORTS
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistroForm
from django.contrib.auth import authenticate, login


# VIEWS

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
# user profile

from django.contrib.auth.decorators import login_required
from .forms import PerfilForm

@login_required
def mi_perfil(request):
    # get the actual user's profile
    perfil = request.user.perfil
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('users:mi_perfil')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'users/mi_perfil.html', {
        'form': form,
        'perfil': perfil,
    })