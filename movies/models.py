from django.db import models
from django.contrib.auth.models import User

# MY-LIST MODEL FOR PERSONAL LIST OF FILMS / SERIES

class MiLista(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mi_lista')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Unique to prevent the film to be saved multiple times
        unique_together = ('user', 'movie_id')

    def __str__(self):
        return f"{self.user.username} - {self.movie_title}"
    
    
# REVIEW MODEL FOR WEBSOCKET CHAT

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, f"{i} estrellas") for i in range(1, 6)])
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # To allow multiple comments from same user we evade using unique treat

    def __str__(self):
        if self.parent:
            return f"Respuesta de {self.user.username} a {self.parent.user.username}"
        return f"Reseña de {self.user.username} para {self.movie_title}"