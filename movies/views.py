import random
from django.shortcuts import render
from .tmdb_service import get_popular_movies, get_now_playing_movies, get_movie_details, get_top_rated_movies, get_random_popular_movies

# HOMEPAGE FUNCTION 
def index_devolution(request):
    return render(request, 'movies/index.html')

# new version with random movie
def home_api(request):
    
    # get the movies from TMDb
    peliculas_tendencias = get_popular_movies()  # populars
    peliculas_recomendadas = get_now_playing_movies()  # new movies
    peliculas_top = get_top_rated_movies()  # top rated
    peliculas_random = get_random_popular_movies()  # random popular movies from different years
    
    # get a random movie for the hero
    pelicula_aleatoria = None
    if peliculas_tendencias:
        pelicula_aleatoria = random.choice(peliculas_tendencias)
    
    context = {
        'trending_movies': peliculas_tendencias,  
        'recommended_movies': peliculas_recomendadas,
        'top_rated_movies': peliculas_top,
        'random_movies': peliculas_random,  
        'my_list': [],
        'continue_watching': [],
        'hero_movie': pelicula_aleatoria,
    }
    
    return render(request, 'movies/index.html', context)


# DETAILS MOVIE
def detalle_pelicula(request, movie_id):
    
    pelicula = get_movie_details(movie_id)
    
    if not pelicula:
        from django.http import Http404
        raise Http404("Película no encontrada")
    
    return render(request, 'movies/detalle.html', {'pelicula': pelicula})