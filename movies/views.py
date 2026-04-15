import random
from django.shortcuts import render
from .tmdb_service import get_popular_movies, get_now_playing_movies, get_movie_details

# HOMEPAGE FUNCTION 
def index_devolution(request):
    return render(request, 'movies/index.html') # return the homepage (index by default standar)

# new version and random
def home_api(request):
    
    # get the movies from TMDb
    peliculas_tendencias = get_popular_movies()  # populars
    peliculas_recomendadas = get_now_playing_movies()  # new movies
    
    # get a random movie for the hero
    pelicula_aleatoria = None
    if peliculas_tendencias:
        pelicula_aleatoria = random.choice(peliculas_tendencias)  # get a random one
    
    context = {
        'trending_movies': peliculas_tendencias,  
        'recommended_movies': peliculas_recomendadas,  
        'my_list': [],  # now it is empty, need users
        'continue_watching': [],  # now it is empty, need users
        'hero_movie': pelicula_aleatoria,  # random movie every time you refresh
    }
    
    return render(request, 'movies/index.html', context)


# DETAILS MOVIE
def detalle_pelicula(request, movie_id):
    
    pelicula = get_movie_details(movie_id)
    
    if not pelicula:
        from django.http import Http404
        raise Http404("Película no encontrada")
    
    return render(request, 'movies/detalle.html', {'pelicula': pelicula})


# NEW VIEW FOR PLAYING MOVIES
def reproducir_pelicula(request, movie_id):
    
    # Get movie details from TMDb
    pelicula = get_movie_details(movie_id)
    
    if not pelicula:
        from django.http import Http404
        raise Http404("Película no encontrada")
    
    # Render the player template
    return render(request, 'movies/reproductor.html', {
        'movie_id': movie_id,
        'pelicula': pelicula
    })