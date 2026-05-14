from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_api, name='home'),
    path('pelicula/<str:movie_id>/', views.detalle_pelicula, name='detalle_pelicula'),
    path('peliculas/', views.catalogo_peliculas, name='movies'),
    path('mi-lista/', views.mi_lista_view, name='mi_lista'),
    path('api/toggle-lista/', views.toggle_lista, name='toggle_lista'),
    path('series/', views.catalogo_series, name='series'),
    path('serie/<str:series_id>/', views.detalle_serie, name='detalle_serie'),
    path('actor/<int:person_id>/', views.detalle_actor, name='detalle_actor'),
]