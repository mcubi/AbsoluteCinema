from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import re

class RegistroForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField()
    password2 = forms.CharField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=20, required=False)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # La validación de email único se hace ahora sobre el modelo User de Django
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        
        # Solo validamos si el usuario ha escrito algo en el campo.
        if telefono:
            if not re.match(r'^\+?\d{9,15}$', telefono):
                raise forms.ValidationError(
                    "Introduce un número de teléfono válido (solo números, opcional + al inicio)."
                )
    
            if UserProfile.objects.filter(telefono=telefono).exists():
                raise forms.ValidationError("Este teléfono ya está registrado.")
        return telefono


    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    

# *********************************************************************************
# form profile
from .models import UserProfile

class PerfilForm(forms.Form):
    # Campos del modelo User
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Nombre'
            }))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Apellidos'
            }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Correo electrónico'
            }))

    # Campos del modelo UserProfile
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Teléfono'
            }))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition cursor-pointer',
                'accept': 'image/*'
            }))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['telefono'].initial = self.user.perfil.telefono
            self.fields['avatar'].initial = self.user.perfil.avatar

    def save(self):
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        self.user.save()

        self.user.perfil.telefono = self.cleaned_data['telefono']
        if self.cleaned_data.get('avatar'): # Solo actualiza si se sube un nuevo avatar
            self.user.perfil.avatar = self.cleaned_data['avatar']
        self.user.perfil.save()