import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
import json

from .tmdb_service import get_popular_movies, get_now_playing_movies, get_movie_details, get_top_rated_movies, get_random_popular_movies
from .models import MiLista, Review

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
        
    # --- ¡NUEVO! SACAR LOS IDS DE TUS PELÍCULAS GUARDADAS ---
    mis_peliculas_ids = []
    # Verificar si el usuario está autenticado de forma segura
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Esto saca una lista de números con las pelis que has guardado [123, 456...]
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

# --- NUEVA VISTA PARA EL CATÁLOGO DE PELÍCULAS ACTUALIZADA ---
def catalogo_peliculas(request):
    # Miramos si la URL tiene un filtro, si no, por defecto es 'populares'
    filtro = request.GET.get('filtro', 'populares')
    
    if filtro == 'cartelera':
        peliculas = get_now_playing_movies()
    elif filtro == 'valoradas':
        peliculas = get_top_rated_movies()
    else:
        peliculas = get_popular_movies()
        
    return render(request, 'movies/peliculas.html', {
        'movies': peliculas,
        'filtro_actual': filtro # Le pasamos el filtro actual al HTML para iluminar el botón
    })

# --- VISTA DE MI LISTA ACTUALIZADA ---
@login_required # Obligamos a estar logueado para ver la lista
def mi_lista_view(request):
    # 1. Buscamos en tu Base de Datos las pelis que has guardado
    items_guardados = MiLista.objects.filter(user=request.user).order_by('-added_at')
    
    # 2. Por cada peli guardada, le pedimos a TMDB el póster y la info
    peliculas_completas = []
    for item in items_guardados:
        detalles = get_movie_details(item.movie_id)
        if detalles:
            peliculas_completas.append(detalles)
            
    # 3. Se las mandamos a tu diseño de 'mi_lista.html'
    return render(request, 'movies/mi_lista.html', {'mis_peliculas': peliculas_completas})

# --- API PARA AÑADIR/QUITAR DE MI LISTA ---
@login_required
@require_POST
def toggle_lista(request):
    try:
        # Leemos los datos que nos manda tu JavaScript
        data = json.loads(request.body)
        
        # OJO AQUÍ: Forzamos que el ID sea un número entero (int) para evitar fallos
        movie_id = int(data.get('movie_id'))
        movie_title = data.get('movie_title')

        # En vez de buscar solo la primera (.first()), cogemos TODAS las que coincidan
        items_lista = MiLista.objects.filter(user=request.user, movie_id=movie_id)

        if items_lista.exists():
            # Si hay 1, 2 o 50 copias duplicadas por error, .delete() las extermina TODAS de golpe
            items_lista.delete()
            return JsonResponse({'status': 'removed'})
        else:
            # Si no existe ninguna, la creamos
            MiLista.objects.create(
                user=request.user,
                movie_id=movie_id,
                movie_title=movie_title
            )
            return JsonResponse({'status': 'added'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --- API PARA OBTENER RESEÑAS (FALLBACK WEBSOCKET) ---
@require_GET
def get_reviews(request, movie_id):
    try:
        reviews = Review.objects.filter(movie_id=movie_id).select_related('user').order_by('-created_at')
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': review.user.users.avatar.url if hasattr(review.user, 'users') and review.user.users.avatar else '/static/img/default-avatar.png'
            })
        
        return JsonResponse({
            'reviews': reviews_data,
            'count': len(reviews_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --- API PARA AÑADIR RESEÑA (FALLBACK WEBSOCKET) ---
@login_required
@require_POST
def add_review_api(request, movie_id):
    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        content = data.get('content')
        movie_title = data.get('movie_title', '')
        
        if not rating or not content:
            return JsonResponse({'error': 'La puntuación y el contenido son obligatorios'}, status=400)
        
        # Crear nueva reseña
        review = Review.objects.create(
            user=request.user,
            movie_id=movie_id,
            movie_title=movie_title,
            rating=rating,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'review': {
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': review.user.users.avatar.url if hasattr(review.user, 'users') and review.user.users.avatar else '/static/img/default-avatar.png'
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)