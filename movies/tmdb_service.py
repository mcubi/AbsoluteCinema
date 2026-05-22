import requests
import random
from django.conf import settings
from datetime import datetime

# Settings API TMDb
API_KEY = settings.TMDB_API_KEY
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page=1&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_url': BACKDROP_BASE_URL,
                'backdrop_path': movie.get('backdrop_path'),
                'vote_average': movie['vote_average'],
                'vote_count': movie.get('vote_count', 0),
                'release_date': movie.get('release_date', ''),
                'overview': movie.get('overview', ''),
                'original_language': movie.get('original_language', '').upper(),
            })
        return formatted_movies
    return []


def get_now_playing_movies():
    """Películas que están actualmente en cines (NOVEDADES)"""
    url = f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&language=es-ES&page=1&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_url': BACKDROP_BASE_URL,
                'backdrop_path': movie.get('backdrop_path'),
                'vote_average': movie['vote_average'],
                'vote_count': movie.get('vote_count', 0),
                'release_date': movie.get('release_date', ''),
                'overview': movie.get('overview', ''),
                'original_language': movie.get('original_language', '').upper(),
            })
        return formatted_movies
    return []


def get_upcoming_movies():
    """Películas que se estrenarán pronto (PRÓXIMAMENTE)"""
    url = f"{BASE_URL}/movie/upcoming?api_key={API_KEY}&language=es-ES&page=1&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_url': BACKDROP_BASE_URL,
                'backdrop_path': movie.get('backdrop_path'),
                'vote_average': movie['vote_average'],
                'vote_count': movie.get('vote_count', 0),
                'release_date': movie.get('release_date', ''),
                'overview': movie.get('overview', ''),
                'original_language': movie.get('original_language', '').upper(),
            })
        return formatted_movies
    return []


def get_top_rated_movies():
    url = f"{BASE_URL}/movie/top_rated?api_key={API_KEY}&language=es-ES&page=1&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_url': BACKDROP_BASE_URL,
                'backdrop_path': movie.get('backdrop_path'),
                'vote_average': movie['vote_average'],
                'vote_count': movie.get('vote_count', 0),
                'release_date': movie.get('release_date', ''),
                'overview': movie.get('overview', ''),
                'original_language': movie.get('original_language', '').upper(),
            })
        return formatted_movies
    return []


def filtrar_por_certificacion(peliculas):
    
    peliculas_filtradas = []
    
    for pelicula in peliculas:
        movie_id = pelicula['id']
        url = f"{BASE_URL}/movie/{movie_id}/release_dates?api_key={API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            certificaciones = data.get('results', [])
            
            certificacion_x = False
            for pais in certificaciones:
                if pais.get('iso_3166_1') == 'ES':
                    for release in pais.get('release_dates', []):
                        if release.get('certification') == 'X':
                            certificacion_x = True
                            break
                    break
            
            if not certificacion_x:
                peliculas_filtradas.append(pelicula)
        else:
            peliculas_filtradas.append(pelicula)
    
    return peliculas_filtradas


def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits,watch/providers,videos&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
                    'id': actor.get('id'),
                    'name': actor.get('name'),
                    'character': actor.get('character'),
                    'profile_path': actor.get('profile_path'),
                })
        
        director = None
        if 'credits' in data and 'crew' in data['credits']:
            for crew_member in data['credits']['crew']:
                if crew_member.get('job') == 'Director':
                    director = crew_member.get('name')
                    break
        
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append({
                    'id': genre.get('id'),
                    'name': genre.get('name'),
                })

        providers = []
        if 'watch/providers' in data and 'results' in data['watch/providers']:
            es_data = data['watch/providers']['results'].get('ES', {})
            if 'flatrate' in es_data:
                for prov in es_data['flatrate']:
                    providers.append({
                        'name': prov.get('provider_name'),
                        'logo_url': f"https://image.tmdb.org/t/p/original{prov.get('logo_path')}" if prov.get('logo_path') else None
                    })
                    
        trailer_key = None
        if 'videos' in data and 'results' in data['videos']:
            for video in data['videos']['results']:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    trailer_key = video.get('key')
                    break
        
        # Calcular estado de estreno
        release_date_str = data.get('release_date', '')
        status = "Estrenada"
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                today = datetime.now().date()
                if release_date > today:
                    status = "Próximamente"
            except ValueError:
                pass
        
        movie_details = {
            'id': data.get('id'),
            'title': data.get('title'),
            'tagline': data.get('tagline'),
            'overview': data.get('overview'),
            'poster_path': data.get('poster_path'),
            'backdrop_path': data.get('backdrop_path'),
            'poster_url': f"{POSTER_BASE_URL}{data['poster_path']}" if data.get('poster_path') else None,
            'backdrop_url': BACKDROP_BASE_URL,
            'vote_average': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'release_date': release_date_str,
            'runtime': data.get('runtime', 0),
            'original_language': data.get('original_language', '').upper(),
            'genres': genres,
            'cast': cast,
            'director': director,
            'providers': providers,
            'trailer_key': trailer_key,
            'status': status,
        }
        return movie_details
    
    return None


def get_random_popular_movies(limit=10):
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2019, 2018, 2017, 2016]
    random_years = random.sample(years, min(5, len(years)))
    
    all_movies = []
    
    for year in random_years:
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&language=es-ES&sort_by=popularity.desc&primary_release_year={year}&page=1&include_adult=false"
        response = requests.get(url)
        
        if response.status_code == 200:
            movies = response.json().get('results', [])[:4]
            for movie in movies:
                all_movies.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                    'backdrop_url': BACKDROP_BASE_URL,
                    'backdrop_path': movie.get('backdrop_path'),
                    'vote_average': movie['vote_average'],
                    'vote_count': movie.get('vote_count', 0),
                    'release_date': movie.get('release_date', ''),
                    'overview': movie.get('overview', ''),
                    'original_language': movie.get('original_language', '').upper(),
                })
    
    random.shuffle(all_movies)
    all_movies = filtrar_por_certificacion(all_movies)
    
    return all_movies[:limit]


# --- FUNCIÓN PARA SERIES ---
# --- FUNCIÓN PARA SERIES (CORREGIDA - ordena por fecha más reciente en 'emision') ---
def get_tv_shows(filtro='populares', page=1, genre_id=None):
    """Obtiene series según el filtro: 'populares', 'valoradas', o 'emision'"""
    
    if filtro == 'emision':
        # Para 'emision' usamos discover con sort_by=first_air_date.desc para obtener las más nuevas
        url = f"{BASE_URL}/discover/tv?api_key={API_KEY}&language=es-ES&page={page}&include_adult=false&sort_by=first_air_date.desc"
        
        # Filtro adicional: solo series que ya han empezado (fecha <= hoy)
        today = datetime.now().date()
        url += f"&first_air_date.lte={today}"
        
        # Opcional: filtrar series que no han terminado (status=Returning Series)
        # Esto no se puede hacer directamente en discover, pero podemos filtrar después
        
        if genre_id:
            url += f"&with_genres={genre_id}"
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            series = data.get('results', [])[:20]
            formatted_series = []
            for show in series:
                # Validar que la serie esté en emisión (opcional, basado en fecha)
                first_air = show.get('first_air_date', '')
                if first_air:
                    try:
                        first_air_date = datetime.strptime(first_air, '%Y-%m-%d').date()
                        if first_air_date > today:
                            continue  # Saltar series que aún no se han estrenado
                    except ValueError:
                        pass
                
                formatted_series.append({
                    'id': show['id'],
                    'title': show.get('name', 'Sin título'),
                    'poster_url': f"{POSTER_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                    'backdrop_url': BACKDROP_BASE_URL,
                    'backdrop_path': show.get('backdrop_path'),
                    'vote_average': show.get('vote_average', 0),
                    'vote_count': show.get('vote_count', 0),
                    'release_date': show.get('first_air_date', ''),
                    'overview': show.get('overview', ''),
                    'original_language': show.get('original_language', '').upper(),
                })
                
            return formatted_series
        except requests.RequestException as e:
            print(f"Error al obtener series en emisión: {e}")
            return []
    
    else:
        # Para 'populares' y 'valoradas' usar los endpoints tradicionales
        endpoints = {
            'populares': 'tv/popular',
            'valoradas': 'tv/top_rated',
        }
        endpoint = endpoints.get(filtro, 'tv/popular')
        url = f"{BASE_URL}/{endpoint}?api_key={API_KEY}&language=es-ES&page={page}&include_adult=false"
        
        if genre_id:
            url += f"&with_genres={genre_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            series = data.get('results', [])[:20]
            formatted_series = []
            for show in series:
                formatted_series.append({
                    'id': show['id'],
                    'title': show.get('name', 'Sin título'),
                    'poster_url': f"{POSTER_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                    'backdrop_url': BACKDROP_BASE_URL,
                    'backdrop_path': show.get('backdrop_path'),
                    'vote_average': show.get('vote_average', 0),
                    'vote_count': show.get('vote_count', 0),
                    'release_date': show.get('first_air_date', ''),
                    'overview': show.get('overview', ''),
                    'original_language': show.get('original_language', '').upper(),
                })
                
            return formatted_series
        except requests.RequestException as e:
            print(f"Error al obtener series ({filtro}): {e}")
            return []


# --- FUNCIÓN PARA DETALLE DE SERIES ---
def get_tv_show_details(series_id):
    url = f"{BASE_URL}/tv/{series_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits,watch/providers,videos&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
                    'id': actor.get('id'),
                    'name': actor.get('name'),
                    'character': actor.get('character'),
                    'profile_path': actor.get('profile_path'),
                })
        
        director = None
        if 'created_by' in data and len(data['created_by']) > 0:
            director = data['created_by'][0].get('name')
        
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append({'id': genre.get('id'), 'name': genre.get('name')})

        providers = []
        if 'watch/providers' in data and 'results' in data['watch/providers']:
            es_data = data['watch/providers']['results'].get('ES', {})
            if 'flatrate' in es_data:
                for prov in es_data['flatrate']:
                    providers.append({
                        'name': prov.get('provider_name'),
                        'logo_url': f"https://image.tmdb.org/t/p/original{prov.get('logo_path')}" if prov.get('logo_path') else None
                    })
                    
        trailer_key = None
        if 'videos' in data and 'results' in data['videos']:
            for video in data['videos']['results']:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    trailer_key = video.get('key')
                    break
        
        # Calcular estado de emisión
        first_air_date_str = data.get('first_air_date', '')
        status_text = "Estrenada"
        if first_air_date_str:
            try:
                first_air_date = datetime.strptime(first_air_date_str, '%Y-%m-%d').date()
                today = datetime.now().date()
                if first_air_date > today:
                    status_text = "Próximamente"
            except ValueError:
                pass
        
        # Usar el status de la API si está disponible
        api_status = data.get('status', '')
        if api_status == 'Returning Series':
            status_text = "En Emisión"
        elif api_status == 'Planned' or api_status == 'In Production':
            if first_air_date_str:
                try:
                    first_air_date = datetime.strptime(first_air_date_str, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    if first_air_date > today:
                        status_text = "Próximamente"
                except ValueError:
                    status_text = "Próximamente"
            else:
                status_text = "Próximamente"
        
        movie_details = {
            'id': data.get('id'),
            'title': data.get('name'),
            'tagline': data.get('tagline'),
            'overview': data.get('overview'),
            'poster_path': data.get('poster_path'),
            'backdrop_path': data.get('backdrop_path'),
            'poster_url': f"{POSTER_BASE_URL}{data['poster_path']}" if data.get('poster_path') else None,
            'backdrop_url': BACKDROP_BASE_URL,
            'vote_average': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'release_date': first_air_date_str,
            'runtime': data.get('episode_run_time', [0])[0] if data.get('episode_run_time') else 0,
            'original_language': data.get('original_language', '').upper(),
            'genres': genres,
            'cast': cast,
            'director': director,
            'providers': providers,
            'trailer_key': trailer_key,
            'number_of_seasons': data.get('number_of_seasons'),
            'number_of_episodes': data.get('number_of_episodes'),
            'status': status_text,
        }
        return movie_details
    return None


def get_person_details(person_id):
    url = f"{BASE_URL}/person/{person_id}?api_key={API_KEY}&language=es-ES&append_to_response=combined_credits"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        filmografia = []
        if 'combined_credits' in data and 'cast' in data['combined_credits']:
            peliculas = data['combined_credits']['cast']
            peliculas.sort(key=lambda x: x.get('release_date', '') or x.get('first_air_date', ''), reverse=True)
            
            for pelicula in peliculas:  
                filmografia.append({
                    'id': pelicula.get('id'),
                    'title': pelicula.get('title') or pelicula.get('name', 'Sin título'),
                    'poster_url': f"{POSTER_BASE_URL}{pelicula.get('poster_path')}" if pelicula.get('poster_path') else None,
                    'character': pelicula.get('character', ''),
                    'release_date': pelicula.get('release_date', '') or pelicula.get('first_air_date', ''),
                    'vote_average': pelicula.get('vote_average', 0),
                    'media_type': pelicula.get('media_type', 'movie'),
                })
        
        known_for_department = data.get('known_for_department', 'Actuación')
        
        dept_traducciones = {
            'Acting': 'Actuación',
            'Directing': 'Dirección',
            'Production': 'Producción',
            'Writing': 'Guion',
            'Editing': 'Montaje',
            'Camera': 'Fotografía',
            'Sound': 'Sonido',
            'Art': 'Dirección de arte',
            'Costume & Make-Up': 'Vestuario y maquillaje',
            'Visual Effects': 'Efectos visuales',
            'Crew': 'Equipo técnico',
            'Creator': 'Creador'
        }
        departamento = dept_traducciones.get(known_for_department, known_for_department)
        
        person_details = {
            'id': data.get('id'),
            'name': data.get('name'),
            'biography': data.get('biography', 'No hay biografía disponible en español.'),
            'birthday': data.get('birthday'),
            'place_of_birth': data.get('place_of_birth'),
            'deathday': data.get('deathday'),
            'profile_path': data.get('profile_path'),
            'profile_url': f"{POSTER_BASE_URL}{data['profile_path']}" if data.get('profile_path') else None,
            'known_for_department': departamento,
            'popularity': data.get('popularity', 0),
            'filmography': filmografia,
        }
        return person_details
    return None


def get_movie_genres():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=es-ES"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('genres', [])
    except requests.RequestException as e:
        print(f"Error al obtener géneros de películas: {e}")
        return []


def get_tv_genres():
    url = f"{BASE_URL}/genre/tv/list?api_key={API_KEY}&language=es-ES"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('genres', [])
    except requests.RequestException as e:
        print(f"Error al obtener géneros de series: {e}")
        return []


def get_watch_providers(media_type='movie'):
    url = f"{BASE_URL}/watch/providers/{media_type}?api_key={API_KEY}&language=es-ES&watch_region=ES"
    try:
        response = requests.get(url)
        response.raise_for_status()
        providers = sorted(
            response.json().get('results', []),
            key=lambda p: p.get('display_priority', 999)
        )
        return providers
    except requests.RequestException as e:
        print(f"Error al obtener proveedores de streaming: {e}")
        return []


def discover_movies(sort_by='populares', genre=None, page=1):
    """Descubre películas con filtros (NO acepta provider para evitar errores)"""
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&language=es-ES&page={page}&include_adult=false"

    sort_map = {
        'populares': 'popularity.desc',
        'valoradas': 'vote_average.desc',
        'cartelera': 'primary_release_date.desc'
    }
    url += f"&sort_by={sort_map.get(sort_by, 'popularity.desc')}"

    if sort_by == 'valoradas':
        url += "&vote_count.gte=200"

    if genre:
        url += f"&with_genres={genre}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get('results', [])
        return [
            {
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'vote_average': movie['vote_average'],
                'release_date': movie.get('release_date', ''),
            } for movie in movies
        ]
    except requests.RequestException as e:
        print(f"Error en discover_movies: {e}")
        return []


def discover_tv_shows(sort_by='populares', genre=None, provider=None, page=1):
    url = f"{BASE_URL}/discover/tv?api_key={API_KEY}&language=es-ES&page={page}&include_adult=false"

    sort_map = {
        'populares': 'popularity.desc',
        'valoradas': 'vote_average.desc',
        'emision': 'first_air_date.desc'
    }
    url += f"&sort_by={sort_map.get(sort_by, 'popularity.desc')}"

    if sort_by == 'valoradas':
        url += "&vote_count.gte=100"

    if genre:
        url += f"&with_genres={genre}"

    if provider:
        url += f"&with_watch_providers={provider}&watch_region=ES"

    try:
        response = requests.get(url)
        response.raise_for_status()
        series = response.json().get('results', [])
        return [
            {
                'id': show['id'],
                'title': show.get('name', 'Sin título'),
                'poster_url': f"{POSTER_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                'vote_average': show.get('vote_average', 0),
                'release_date': show.get('first_air_date', ''),
            } for show in series
        ]
    except requests.RequestException as e:
        print(f"Error en discover_tv_shows: {e}")
        return []


def search_movies(query, page=1):
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&language=es-ES&query={query}&page={page}&include_adult=false"
    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get('results', [])
        return [
            {
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'vote_average': movie['vote_average'],
                'release_date': movie.get('release_date', ''),
            } for movie in movies
        ]
    except requests.RequestException as e:
        print(f"Error en search_movies: {e}")
        return []


def search_tv_shows(query, page=1):
    url = f"{BASE_URL}/search/tv?api_key={API_KEY}&language=es-ES&query={query}&page={page}&include_adult=false"
    try:
        response = requests.get(url)
        response.raise_for_status()
        series = response.json().get('results', [])
        return [
            {
                'id': show['id'],
                'title': show.get('name', 'Sin título'),
                'poster_url': f"{POSTER_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                'vote_average': show.get('vote_average', 0),
                'release_date': show.get('first_air_date', ''),
            } for show in series
        ]
    except requests.RequestException as e:
        print(f"Error en search_tv_shows: {e}")
        return []