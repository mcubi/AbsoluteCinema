import requests
import random
from django.conf import settings

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
        # call to obtain movies certifications
        url = f"{BASE_URL}/movie/{movie_id}/release_dates?api_key={API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            certificaciones = data.get('results', [])
            
            # search the spanish certification
            certificacion_x = False
            for pais in certificaciones:
                if pais.get('iso_3166_1') == 'ES':
                    for release in pais.get('release_dates', []):
                        if release.get('certification') == 'X':
                            certificacion_x = True
                            break
                    break
            
            # if it has not an x certification, we keep it
            if not certificacion_x:
                peliculas_filtradas.append(pelicula)
        else:
            
            peliculas_filtradas.append(pelicula)
    
    return peliculas_filtradas


def get_movie_details(movie_id):
    # Hemos añadido ",videos" al final de la URL para traer los trailers
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits,watch/providers,videos&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # CAST
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
                    'id': actor.get('id'),  # id actor
                    'name': actor.get('name'),
                    'character': actor.get('character'),
                    'profile_path': actor.get('profile_path'),
                })
        
        # --- DIRECTOR ---
        director = None
        if 'credits' in data and 'crew' in data['credits']:
            for crew_member in data['credits']['crew']:
                if crew_member.get('job') == 'Director':
                    director = crew_member.get('name')
                    break
        
        # --- GÉNEROS ---
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append({
                    'id': genre.get('id'),
                    'name': genre.get('name'),
                })

        # --- PLATAFORMAS DE STREAMING (ESPAÑA) ---
        providers = []
        if 'watch/providers' in data and 'results' in data['watch/providers']:
            # Buscamos 'ES' para España (si quieres de otro país, cambia el código)
            es_data = data['watch/providers']['results'].get('ES', {})
            
            # 'flatrate' significa que está en suscripción mensual (Netflix, Max, Prime, etc.)
            if 'flatrate' in es_data:
                for prov in es_data['flatrate']:
                    providers.append({
                        'name': prov.get('provider_name'),
                        'logo_url': f"https://image.tmdb.org/t/p/original{prov.get('logo_path')}" if prov.get('logo_path') else None
                    })
                    
        # --- TRÁILER ---
        trailer_key = None
        if 'videos' in data and 'results' in data['videos']:
            for video in data['videos']['results']:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    trailer_key = video.get('key')
                    break # Nos quedamos con el primero que encuentre
        
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
            'release_date': data.get('release_date', ''),
            'runtime': data.get('runtime', 0),
            'original_language': data.get('original_language', '').upper(),
            'genres': genres,
            'cast': cast,
            'director': director,
            'providers': providers,
            'trailer_key': trailer_key, # <-- Añadimos la clave del vídeo aquí
        }
        return movie_details
    
    return None


# for the random movies
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
    
    # suffle for the movies
    random.shuffle(all_movies)
    
    # Filter movies with X certification
    all_movies = filtrar_por_certificacion(all_movies)
    
    return all_movies[:limit]


# --- FUNCIÓN PARA SERIES ---
def get_tv_shows(filtro='populares', page=1):
    endpoints = {
        'populares': 'tv/popular',
        'valoradas': 'tv/top_rated',
        'emision': 'tv/on_the_air'
    }
    
    endpoint = endpoints.get(filtro, 'tv/popular')
    url = f"{BASE_URL}/{endpoint}?api_key={API_KEY}&language=es-ES&page={page}&include_adult=false"
    
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
    # ¡NUEVO! Hemos añadido ",videos" al final de la URL
    url = f"{BASE_URL}/tv/{series_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits,watch/providers,videos&include_adult=false"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
                    'id': actor.get('id'),  # actor id
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
                    
        # --- TRÁILER ---
        trailer_key = None
        if 'videos' in data and 'results' in data['videos']:
            for video in data['videos']['results']:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    trailer_key = video.get('key')
                    break
        
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
            'release_date': data.get('first_air_date', ''),
            'runtime': data.get('episode_run_time', [0])[0] if data.get('episode_run_time') else 0,
            'original_language': data.get('original_language', '').upper(),
            'genres': genres,
            'cast': cast,
            'director': director,
            'providers': providers,
            'trailer_key': trailer_key, # <-- Añadimos la clave del vídeo aquí
            'number_of_seasons': data.get('number_of_seasons'),   # <-- TEMPORADAS
            'number_of_episodes': data.get('number_of_episodes'), # <-- EPISODIOS
        }
        return movie_details
    return None

# ******************************************************************************************************************

# details of the actor
def get_person_details(person_id):
    url = f"{BASE_URL}/person/{person_id}?api_key={API_KEY}&language=es-ES&append_to_response=combined_credits"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # movies they worked in
        filmografia = []
        if 'combined_credits' in data and 'cast' in data['combined_credits']:
            # the newest to the oldest
            peliculas = data['combined_credits']['cast']
            peliculas.sort(key=lambda x: x.get('release_date', ''), reverse=True)
            
            for pelicula in peliculas[:20]:  # only 20
                filmografia.append({
                    'id': pelicula.get('id'),
                    'title': pelicula.get('title') or pelicula.get('name', 'Sin título'),
                    'poster_url': f"{POSTER_BASE_URL}{pelicula.get('poster_path')}" if pelicula.get('poster_path') else None,
                    'character': pelicula.get('character', ''),
                    'release_date': pelicula.get('release_date', '') or pelicula.get('first_air_date', ''),
                    'vote_average': pelicula.get('vote_average', 0),
                    'media_type': pelicula.get('media_type', 'movie'),  # movie or tv
                })
        
        # what they do
        known_for_department = data.get('known_for_department', 'Actuación')
        
        # to spanish
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