# IMPORTS
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistroForm


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


     
# log - in::  WARNING! no functional
def login_user(request):
   return render(request, 'users/login.html')