# IMPORTS: 
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.forms import UserChangeForm # DEUD! | future changes


# VIEWS:


# JUST SHOWING - NO LOGIC NOW

# registration::
def register_user(request):
   return render(request, 'users/register.html')

# log-in::
def login_user(request):
    return render(request, 'users/login.html')