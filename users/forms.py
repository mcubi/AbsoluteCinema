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
    telefono = forms.CharField(max_length=20)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

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

class PerfilForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        
        #get the things we can edit
        fields = ['first_name', 'last_name', 'email', 'telefono', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Correo electrónico'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition',
                'placeholder': 'Teléfono'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full bg-[#1a1a1a] border border-white/20 rounded-lg px-4 py-3 text-white focus:border-ac-primary focus:outline-none transition cursor-pointer',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # check if there is a user profile
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email
            self.fields['telefono'].initial = self.instance.telefono