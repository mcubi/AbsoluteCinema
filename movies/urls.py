from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_api, name='home'),
    path('pelicula/<int:movie_id>/', views.detalle_pelicula, name='detalle_pelicula'),
]