from django.contrib import admin
from .models import Review, MiLista

# REVIEW REGISTRATION:
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_title', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'movie_title', 'content')
    ordering = ('-created_at',)
    
# MY-LIST REGISTRATION: 
@admin.register(MiLista)
class MiListaAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_title', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'movie_title')
    ordering = ('-added_at',)
