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
