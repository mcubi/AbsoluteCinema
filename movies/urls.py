from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_api, name='home'),
    path('pelicula/<int:movie_id>/', views.detalle_pelicula, name='detalle_pelicula'),
    path('peliculas/', views.catalogo_peliculas, name='movies'),
    path('mi-lista/', views.mi_lista_view, name='mi_lista'),
    path('api/toggle-lista/', views.toggle_lista, name='toggle_lista'),
]