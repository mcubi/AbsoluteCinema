import random
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .tmdb_service import get_popular_movies, get_now_playing_movies, get_movie_details, get_top_rated_movies, get_random_popular_movies, get_tv_shows, get_tv_show_details, get_person_details, get_movie_genres, get_tv_genres, discover_movies, discover_tv_shows, search_movies, search_tv_shows
from .models import MiLista, Review

# HOMEPAGE FUNCTION 
def index_devolution(request):
    return render(request, 'movies/index.html')

# new version with random movie AND 6 SECTIONS
def home_api(request):
    # --- 1. PELÍCULAS ---
    peliculas_tendencias = get_popular_movies()
    peliculas_recomendadas = get_now_playing_movies()
    peliculas_top = get_top_rated_movies()
    peliculas_random = get_random_popular_movies()
    
    # --- 2. SERIES (Con el truco del ID negativo) ---
    def formatear_series(lista):
        for s in lista:
            if 'id' in s:
                s['id'] = -abs(s['id'])
        return lista

    series_populares = formatear_series(get_tv_shows('populares'))
    series_emision = formatear_series(get_tv_shows('emision'))
    series_top = formatear_series(get_tv_shows('valoradas'))
    
    # --- 3. HERO (Imagen principal) ---
    todo_popular = peliculas_tendencias + series_populares
    hero_item = random.choice(todo_popular) if todo_popular else None

    # --- 4. IDs GUARDADOS ---
    mis_peliculas_ids = []
    if request.user.is_authenticated:
        # Esto saca una lista de números con las pelis que has guardado [123, 456...]
        mis_peliculas_ids = list(MiLista.objects.filter(user=request.user).values_list('movie_id', flat=True))
    
    context = {
        'trending_movies': peliculas_tendencias,  
        'series_populares': series_populares,
        'recommended_movies': peliculas_recomendadas,
        'series_emision': series_emision,
        'top_rated_movies': peliculas_top,
        'series_top': series_top,
        'random_movies': peliculas_random,
        'hero_movie': hero_item,
        'mis_peliculas_ids': mis_peliculas_ids,
    }
    
    return render(request, 'movies/index.html', context)


# DETAILS MOVIE
def detalle_pelicula(request, movie_id):
    # Convertimos a int por seguridad
    movie_id = int(movie_id)
    
    # EL REDIRECCIONADOR REAL: Si llega un negativo, significa que es una serie
    if movie_id < 0:
        return redirect('detalle_serie', series_id=abs(movie_id))
        
    pelicula = get_movie_details(movie_id)
    
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
    query = request.GET.get('q')
    
    # Obtener la lista de géneros para el desplegable
    generos = get_movie_genres()

    if query:
        # Si hay una consulta de búsqueda, buscamos por nombre
        peliculas = search_movies(query)
    else:
        # Si no, usamos los filtros de descubrimiento
        peliculas = discover_movies(sort_by=filtro_actual, genre=genero_actual)

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
        'query': query,
    })

# --- VISTA DE MI LISTA ---
@login_required 
def mi_lista_view(request):
    # 1. Buscamos en tu Base de Datos las pelis que has guardado
    items_guardados = MiLista.objects.filter(user=request.user).order_by('-added_at')
    
    # 2. Por cada peli guardada, le pedimos a TMDB el póster y la info
    peliculas_completas = []
    for item in items_guardados:
        if item.movie_id < 0:
            detalles = get_tv_show_details(abs(item.movie_id))
            if detalles:
                detalles['es_serie'] = True 
                detalles['id'] = item.movie_id # Mantenemos el negativo para que funcione la papelera
        else:
            detalles = get_movie_details(item.movie_id)
            if detalles:
                detalles['id'] = item.movie_id
                
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
    query = request.GET.get('q')

    # Obtener la lista de géneros de series para el desplegable
    generos = get_tv_genres()

    if query:
        # Si hay una consulta de búsqueda, buscamos por nombre
        series = search_tv_shows(query)
    else:
        # Si no, usamos los filtros de descubrimiento
        series = discover_tv_shows(sort_by=filtro_actual, genre=genero_actual)

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
        'query': query,
    })

# --- DETALLE DE SERIES ---
def detalle_serie(request, series_id):
    series_id = int(series_id)
    serie = get_tv_show_details(series_id)
    
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
            mis_peliculas_ids = {-abs(series_id)} # Le mandamos el negativo al HTML para que pinte el tick
    
    return render(request, 'movies/detalle.html', {
        'pelicula': serie,
        'mis_peliculas_ids': mis_peliculas_ids
    })
    
# details of the actor
def detalle_actor(request, person_id):
    """
    Vista para mostrar los detalles de un actor o persona
    """
    person_id = int(person_id)
    persona = get_person_details(person_id)
    
    if not persona:
        from django.http import Http404
        raise Http404("Persona no encontrada")
    
    return render(request, 'movies/actor.html', {
        'persona': persona,
    })

    
# WEBSOCKET VIEW FUNCTION:


# GET REV

# --- API PARA OBTENER RESEÑAS (FALLBACK WEBSOCKET) ---
@require_GET
def get_reviews_api(request, movie_id):
    try:
        movie_id = int(movie_id)
        # Get only top-level reviews (no parent)
        reviews = Review.objects.filter(movie_id=movie_id, parent=None).select_related('user').order_by('-created_at')
        
        reviews_data = []
        for review in reviews:
            # Get replies for this review
            replies = Review.objects.filter(parent=review).select_related('user').order_by('created_at')
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