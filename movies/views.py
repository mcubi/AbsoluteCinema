import random
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.cache import cache  # IMPRESCINDIBLE PARA REDIS
from .tmdb_service import (
    get_popular_movies, get_now_playing_movies, get_movie_details, 
    get_top_rated_movies, get_random_popular_movies, get_tv_shows, 
    get_tv_show_details, get_person_details, get_movie_genres, 
    get_tv_genres, discover_movies, discover_tv_shows, search_movies, 
    search_tv_shows, get_watch_providers
)
from .models import MiLista, Review

# HOMEPAGE FUNCTION 
def index_devolution(request):
    return render(request, 'movies/index.html')


# VISTA HOME: Cacheamos los datos globales de la API de TMDb durante 15 minutos
def home_api(request):
    # Intentamos sacar todo el pack de TMDb de la caché de Redis
    cache_key = "home_api_tmdb_data"
    cached_data = cache.get(cache_key)
    
    if not cached_data:
        # Si no está guardado, hacemos las llamadas pesadas una sola vez
        peliculas_tendencias = get_popular_movies()
        peliculas_recomendadas = get_now_playing_movies()
        peliculas_top = get_top_rated_movies()
        peliculas_random = get_random_popular_movies()
        
        def formatear_series(lista):
            for s in lista:
                if 'id' in s:
                    s['id'] = -abs(s['id'])
            return lista

        series_populares = formatear_series(get_tv_shows('populares'))
        series_emision = formatear_series(get_tv_shows('emision'))
        series_top = formatear_series(get_tv_shows('valoradas'))
        
        todo_popular = peliculas_tendencias + series_populares
        hero_item = random.choice(todo_popular) if todo_popular else None
        
        cached_data = {
            'trending_movies': peliculas_tendencias,
            'series_populares': series_populares,
            'recommended_movies': peliculas_recomendadas,
            'series_emision': series_emision,
            'top_rated_movies': peliculas_top,
            'series_top': series_top,
            'random_movies': peliculas_random,
            'hero_movie': hero_item,
        }
        # Lo guardamos en Redis por 15 minutos (900 segundos)
        cache.set(cache_key, cached_data, 900)

    # Las películas guardadas NO se cachean de forma global porque dependen de cada usuario
    mis_peliculas_ids = []
    if request.user.is_authenticated:
        mis_peliculas_ids = list(MiLista.objects.filter(user=request.user).values_list('movie_id', flat=True))
    
    context = {**cached_data, 'mis_peliculas_ids': mis_peliculas_ids}
    return render(request, 'movies/index.html', context)


# DETAILS MOVIE: Cacheamos los detalles individuales por película
def detalle_pelicula(request, movie_id):
    # Convertimos a int por seguridad
    movie_id = int(movie_id)
    
    # EL REDIRECCIONADOR REAL: Si llega un negativo, significa que es una serie
    if movie_id < 0:
        return redirect('detalle_serie', series_id=abs(movie_id))
        
    # Clave única para cada película en la caché
    cache_key = f"movie_detail_{movie_id}"
    pelicula = cache.get(cache_key)
    
    if not pelicula:
        pelicula = get_movie_details(movie_id)
        if pelicula:
            cache.set(cache_key, pelicula, 3600)  # Guardamos 1 hora (no cambia mucho el detalle)
            
    if not pelicula:
        from django.http import Http404
        raise Http404("Película no encontrada")
    
    mis_peliculas_ids = []
    if request.user.is_authenticated:
        mis_peliculas_ids = list(MiLista.objects.filter(user=request.user, movie_id=movie_id).values_list('movie_id', flat=True))
        
    return render(request, 'movies/detalle.html', {
        'pelicula': pelicula,
        'mis_peliculas_ids': mis_peliculas_ids
    })


# --- CATÁLOGO DE PELÍCULAS ---
def catalogo_peliculas(request):
    filtro_actual = request.GET.get('filtro', 'populares')
    genero_actual = request.GET.get('genre')
    provider_actual = request.GET.get('provider')
    query = request.GET.get('q')
    
    # Creamos una clave de caché única según los filtros dinámicos que use el usuario
    cache_key = f"catalogo_movies_{filtro_actual}_{genero_actual}_{provider_actual}_{query}"
    cached_catalog = cache.get(cache_key)
    
    if cached_catalog:
        generos = cached_catalog['genres']
        providers = cached_catalog['providers']
        peliculas = cached_catalog['movies']
    else:
        generos = get_movie_genres()
        providers = get_watch_providers('movie')
        if query:
            peliculas = search_movies(query)
        else:
            peliculas = discover_movies(sort_by=filtro_actual, genre=genero_actual, provider=provider_actual)
            
        # Almacenamos los resultados de TMDb por 10 minutos
        cache.set(cache_key, {'genres': generos, 'providers': providers, 'movies': peliculas}, 600)

    mis_peliculas_ids = []
    if request.user.is_authenticated:
        # Aquí solo queremos las pelis (IDs positivos)
        mis_peliculas_ids = list(MiLista.objects.filter(user=request.user, movie_id__gt=0).values_list('movie_id', flat=True))
        
    return render(request, 'movies/peliculas.html', {
        'movies': peliculas,
        'filtro_actual': filtro_actual,
        'mis_peliculas_ids': mis_peliculas_ids,
        'genres': generos,
        'current_genre': genero_actual,
        'providers': providers,
        'current_provider': provider_actual,
        'query': query,
    })


# --- VISTA DE MI LISTA: Turbo activado ---
@login_required 
def mi_lista_view(request):
    # 1. Buscamos en tu Base de Datos las pelis que has guardado
    items_guardados = MiLista.objects.filter(user=request.user).order_by('-added_at')
    
    # 2. Por cada peli guardada, le pedimos a TMDB el póster y la info
    peliculas_completas = []
    
    for item in items_guardados:
        # Cacheamos la información de la película individualmente por ID para no colapsar TMDb
        cache_key = f"milista_item_info_{item.movie_id}"
        detalles = cache.get(cache_key)
        
        if not detalles:
            if item.movie_id < 0:
                detalles = get_tv_show_details(abs(item.movie_id))
                if detalles:
                    detalles['es_serie'] = True 
                    detalles['id'] = item.movie_id
            else:
                detalles = get_movie_details(item.movie_id)
                if detalles:
                    detalles['id'] = item.movie_id
            
            if detalles:
                # Guardamos la ficha en caché 30 minutos (los pósters/sinopsis no van a cambiar en este rato)
                cache.set(cache_key, detalles, 1800)
                
        if detalles:
            peliculas_completas.append(detalles)
            
    # 3. Se las mandamos a tu diseño de 'mi_lista.html'
    return render(request, 'movies/mi_lista.html', {'mis_peliculas': peliculas_completas})


# --- API PARA AÑADIR/QUITAR ---
@login_required
@require_POST
def toggle_lista(request):
    try:
        # Leemos los datos que nos manda tu JavaScript
        data = json.loads(request.body)
        
        # OJO AQUÍ: Forzamos que el ID sea un número entero (int) para evitar fallos
        movie_id = int(data.get('movie_id'))
        movie_title = data.get('movie_title')
        
        # Si se le da al botón desde la página de Detalles de una serie, lo forzamos a negativo
        referer = request.META.get('HTTP_REFERER', '')
        if 'serie' in referer.lower():
            movie_id = -abs(movie_id)

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


# --- CATÁLOGO DE SERIES ---
def catalogo_series(request):
    filtro_actual = request.GET.get('filtro', 'populares')
    genero_actual = request.GET.get('genre')
    provider_actual = request.GET.get('provider')
    query = request.GET.get('q')

    cache_key = f"catalogo_series_{filtro_actual}_{genero_actual}_{provider_actual}_{query}"
    cached_catalog = cache.get(cache_key)
    
    if cached_catalog:
        generos = cached_catalog['genres']
        providers = cached_catalog['providers']
        series = cached_catalog['series']
    else:
        generos = get_tv_genres()
        providers = get_watch_providers('tv')
        if query:
            series = search_tv_shows(query)
        else:
            series = discover_tv_shows(sort_by=filtro_actual, genre=genero_actual, provider=provider_actual)
        cache.set(cache_key, {'genres': generos, 'providers': providers, 'series': series}, 600)

    mis_peliculas_ids = {}
    if request.user.is_authenticated:
        ids_negativos = list(MiLista.objects.filter(user=request.user, movie_id__lt=0).values_list('movie_id', flat=True))
        mis_peliculas_ids = {abs(id) for id in ids_negativos}

    return render(request, 'movies/series.html', {
        'movies': series,
        'filtro_actual': filtro_actual,
        'mis_peliculas_ids': mis_peliculas_ids,
        'genres': generos,
        'current_genre': genero_actual,
        'providers': providers,
        'current_provider': provider_actual,
        'query': query,
    })


# --- DETALLE DE SERIES ---
def detalle_serie(request, series_id):
    series_id = int(series_id)
    cache_key = f"series_detail_{series_id}"
    serie = cache.get(cache_key)
    
    if not serie:
        serie = get_tv_show_details(series_id)
        if serie:
            cache.set(cache_key, serie, 3600)
        
    if not serie:
        from django.http import Http404
        raise Http404("Serie no encontrada")
        
    # FIX DEFINITIVO: Convertimos el ID a negativo aquí directamente para que la plantilla HTML 
    # y el botón de "Mi Lista" sepan sin dudarlo que están tratando con una serie
    serie['id'] = -abs(series_id)
        
    mis_peliculas_ids = set()
    if request.user.is_authenticated:
        # Comprobamos en la base de datos con el ID negativo
        if MiLista.objects.filter(user=request.user, movie_id=-abs(series_id)).exists():
            mis_peliculas_ids = {-abs(series_id)}
    
    return render(request, 'movies/detalle.html', {
        'pelicula': serie,
        'mis_peliculas_ids': mis_peliculas_ids
    })
    

# DETAILS OF THE ACTOR
def detalle_actor(request, person_id):
    """
    Vista para mostrar los detalles de un actor o persona
    """
    person_id = int(person_id)
    cache_key = f"person_detail_{person_id}"
    persona = cache.get(cache_key)
    
    if not persona:
        persona = get_person_details(person_id)
        if persona:
            cache.set(cache_key, persona, 3600)
    
    if not persona:
        from django.http import Http404
        raise Http404("Persona no encontrada")
    
    return render(request, 'movies/actor.html', {
        'persona': persona,
    })


# --- API PARA OBTENER RESEÑAS (OPTIMIZACIÓN ORM N+1) ---
@require_GET
def get_reviews_api(request, movie_id):
    try:
        movie_id = int(movie_id)
        # MEJORA CLAVE: Traemos el user y su perfil de golpe ('user__perfil') en la consulta inicial
        reviews = Review.objects.filter(movie_id=movie_id, parent=None).select_related('user', 'user__perfil').order_by('-created_at')
        
        reviews_data = []
        for review in reviews:
            # MEJORA CLAVE: Hacemos lo mismo para las respuestas de las reseñas
            replies = Review.objects.filter(parent=review).select_related('user', 'user__perfil').order_by('created_at')
            replies_data = []
            for reply in replies:
                replies_data.append({
                    'id': reply.id,
                    'user': reply.user.username,
                    'rating': reply.rating,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%d/%m/%Y %H:%M'),
                    'avatar': reply.user.perfil.avatar.url if hasattr(reply.user, 'perfil') and reply.user.perfil.avatar else '/static/img/default-avatar.png',
                    'parent_id': review.id
                })
            
            reviews_data.append({
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': review.user.perfil.avatar.url if hasattr(review.user, 'perfil') and review.user.perfil.avatar else '/static/img/default-avatar.png',
                'replies': replies_data,
                'reply_count': len(replies_data)
            })
        
        return JsonResponse({
            'reviews': reviews_data,
            'count': len(reviews_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# POST REV

@login_required
@require_POST
def add_review_api(request, movie_id):
    try:
        movie_id = int(movie_id)
        data = json.loads(request.body)
        rating = data.get('rating')
        content = data.get('content')
        movie_title = data.get('movie_title', '')
        parent_id = data.get('parent_id')
        
        if not rating or not content:
            return JsonResponse({'error': 'La puntuación y el contenido son obligatorios'}, status=400)
        
        # If parent_id is provided, validate it exists
        parent_review = None
        if parent_id:
            try:
                parent_review = Review.objects.get(id=parent_id, movie_id=movie_id)
            except Review.DoesNotExist:
                return JsonResponse({'error': 'La reseña padre no existe'}, status=400)
        
        # Crear nueva reseña o respuesta
        review = Review.objects.create(
            user=request.user,
            movie_id=movie_id,
            movie_title=movie_title,
            rating=rating,
            content=content,
            parent=parent_review
        )
        
        response_data = {
            'success': True,
            'review': {
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': review.user.perfil.avatar.url if hasattr(review.user, 'perfil') and review.user.perfil.avatar else '/static/img/default-avatar.png'
            }
        }
        
        if parent_review:
            response_data['review']['parent_id'] = parent_review.id
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_POST
def delete_review_api(request, review_id):
    try:
        review_id = int(review_id)
        review = Review.objects.get(id=review_id)
        
        # Verificar que la reseña pertenece al usuario actual
        if review.user != request.user:
            return JsonResponse({'error': 'No tienes permiso para eliminar esta reseña'}, status=403)
        
        review.delete()
        return JsonResponse({'success': True})
        
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Reseña no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)