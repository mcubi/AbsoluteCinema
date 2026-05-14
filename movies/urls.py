from django.urls import path

from . import views



urlpatterns = [

    path('', views.home_api, name='home'),

    path('pelicula/<int:movie_id>/', views.detalle_pelicula, name='detalle_pelicula'),

    path('peliculas/', views.catalogo_peliculas, name='movies'),

    path('mi-lista/', views.mi_lista_view, name='mi_lista'),

    path('api/toggle-lista/', views.toggle_lista, name='toggle_lista'),

    # API URLs for reviews
    path('api/reviews/<int:movie_id>/', views.get_reviews, name='get_reviews'),
    path('api/reviews/<int:movie_id>/add/', views.add_review_api, name='add_review'),

]