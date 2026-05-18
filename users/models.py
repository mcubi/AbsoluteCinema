# IMPORTS:
from django.db import models
from django.contrib.auth.models import User # *1

# MODELS:

# Model - UserProfile => extends User model (Django default User model *1)
class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil') # 1 profile for every user

    # Must have!
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, unique=True)

    # Optional field:
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.email}" # Self-show on admin

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil_usuario_nuevo(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name or "Sin nombre",
            last_name=instance.last_name or "Sin apellido",
            email=instance.email or f"{instance.username}@example.com",
            # Evitamos el error de campo único generando un valor temporal único por ID
            telefono=f"00000000_{instance.id}" 
        )