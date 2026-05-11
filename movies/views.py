import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .tmdb_service import get_popular_movies, get_now_playing_movies, get_movie_details, get_top_rated_movies, get_random_popular_movies
from .models import MiLista

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
        
    # Getting saved movies ID's
    mis_peliculas_ids = []
    if request.user.is_authenticated:
        
        mis_peliculas_ids = list(MiLista.objects.filter(user=request.user).values_list('movie_id', flat=True))
    
    context = {
        'trending_movies': peliculas_tendencias,  
        'recommended_movies': peliculas_recomendadas,
        'top_rated_movies': peliculas_top,
        'random_movies': peliculas_random,  
        'my_list': [],
        'continue_watching': [],
        'hero_movie': pelicula_aleatoria,
        'mis_peliculas_ids': mis_peliculas_ids, # Pasamos la lista al HTML
    }
    
    return render(request, 'movies/index.html', context)


# DETAILS MOVIE
def detalle_pelicula(request, movie_id):
    
    pelicula = get_movie_details(movie_id)
    
    if not pelicula:
        from django.http import Http404
        raise Http404("Película no encontrada")
    
    return render(request, 'movies/detalle.html', {'pelicula': pelicula})

# Film Catalog View
def catalogo_peliculas(request):
    # We check if the URL has a filter; if not, it defaults to 'popular'.
    filtro = request.GET.get('filtro', 'populares')
    
    if filtro == 'cartelera':
        peliculas = get_now_playing_movies()
    elif filtro == 'valoradas':
        peliculas = get_top_rated_movies()
    else:
        peliculas = get_popular_movies()
        
    return render(request, 'movies/peliculas.html', {
        'movies': peliculas,
        'filtro_actual': filtro # We pass the current filter to the HTML to highlight the button
    })

# My - List view
@login_required # U must be logged
def mi_lista_view(request):
    # 1. Search saved movies in DB
    items_guardados = MiLista.objects.filter(user=request.user).order_by('-added_at')
    
    # 2. For each movie saved, we ask TMDB for the poster and info
    peliculas_completas = []
    for item in items_guardados:
        detalles = get_movie_details(item.movie_id)
        if detalles:
            peliculas_completas.append(detalles)
            
    # 3. Send it to the HTML list
    return render(request, 'movies/mi_lista.html', {'mis_peliculas': peliculas_completas})

# Add / Quit API (movies)
@login_required
@require_POST
def toggle_lista(request):
    try:
        # Read JS data
        data = json.loads(request.body)
        
        # Force ID to be an integer (to evade failures)
        movie_id = int(data.get('movie_id'))
        movie_title = data.get('movie_title')

        # Instead of just looking for the first one (.first()), we take ALL the matching ones
        items_lista = MiLista.objects.filter(user=request.user, movie_id=movie_id)

        if items_lista.exists():
            # If there are 1, 2, or 50 duplicate copies by mistake, .delete() will delete them ALL at once.
            items_lista.delete()
            return JsonResponse({'status': 'removed'})
        else:
            # Case of none, we create it
            MiLista.objects.create(
                user=request.user,
                movie_id=movie_id,
                movie_title=movie_title
            )
            return JsonResponse({'status': 'added'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)