import requests
import random
from django.conf import settings

# Settings API TMDb
API_KEY = settings.TMDB_API_KEY
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

def _format_movie_data(movie):
    """Helper function to format movie data consistently."""
    return {
        'id': movie['id'],
        'title': movie.get('title') or movie.get('name') or 'Sin título',
        'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
        'backdrop_url': BACKDROP_BASE_URL,
        'backdrop_path': movie.get('backdrop_path'),
        'vote_average': movie.get('vote_average', 0),
        'vote_count': movie.get('vote_count', 0),
        'release_date': movie.get('release_date') or movie.get('first_air_date') or '',
        'overview': movie.get('overview', ''),
        'original_language': movie.get('original_language', '').upper(),
    }

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        return [_format_movie_data(movie) for movie in movies]
    return []


def get_now_playing_movies():
    url = f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&language=es-ES&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        return [_format_movie_data(movie) for movie in movies]
    return []


def get_top_rated_movies():
    url = f"{BASE_URL}/movie/top_rated?api_key={API_KEY}&language=es-ES&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])[:20]
        return [_format_movie_data(movie) for movie in movies]
    return []


def get_movie_details(movie_id):
    # Adding ",watch/providers" at the end of the URL
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits,watch/providers"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # --- CAST ---
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
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
        
        # --- GENDERS ---
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append({
                    'id': genre.get('id'),
                    'name': genre.get('name'),
                })

        # STREAMING PLATFORM LANGUAGE -> SPANISH
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
        }
        return movie_details
    
    return None


# for the random movies

def get_random_popular_movies(limit=10):
    
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2019, 2018, 2017, 2016]
    random_years = random.sample(years, min(5, len(years)))
    
    all_movies = []
    
    for year in random_years:
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&language=es-ES&sort_by=popularity.desc&primary_release_year={year}&page=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            movies = response.json().get('results', [])[:4]
            for movie in movies:
                all_movies.append(_format_movie_data(movie))
    
    # suffle for the movies
    random.shuffle(all_movies)
    return all_movies[:limit]

def search_and_filter_movies(query=None, genre_id=None, sort_by='popularity.desc'):
    """
    Searches for movies by name or filters by genre.
    If a query is provided, it uses the /search/movie endpoint.
    If only a genre_id is provided (no query), it uses the /discover/movie endpoint.
    """
    params = {'api_key': API_KEY, 'language': 'es-ES', 'page': 1}
    
    if query:
        params['query'] = query
        url = f"{BASE_URL}/search/multi"
    else:
        url = f"{BASE_URL}/discover/movie"
        params['sort_by'] = sort_by

    if genre_id:
        params['with_genres'] = genre_id

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        # Filter out movies without a poster path for better display in the catalog
        return [_format_movie_data(item) for item in results if item.get('media_type') != 'person' and item.get('poster_path')]
    return []

def get_genres():
    """Fetches the list of movie genres from TMDb."""
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=es-ES"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('genres', [])
    return []