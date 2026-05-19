# IMPORTS:
from django.db import models
from django.contrib.auth.models import User # *1

# MODELS:

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil') # 1 profile for every user

    # Estos campos se duplican para facilitar el acceso, pero la fuente principal es el modelo User.
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Optional field:
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}" # Self-show on admin

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil_usuario_nuevo(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name
        )