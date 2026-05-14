from django.db import models
from django.contrib.auth.models import User

class MiLista(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mi_lista')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Esto evita que un usuario guarde la misma peli dos veces
        unique_together = ('user', 'movie_id')

    def __str__(self):
        return f"{self.user.username} - {self.movie_title}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, f"{i} estrellas") for i in range(1, 6)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Sin unique_together para permitir múltiples reseñas del mismo usuario para la misma película

    def __str__(self):
        return f"Reseña de {self.user.username} para {self.movie_title}"