# Service for interacting with the TMDb (The Movie Database) API
import requests
from django.conf import settings

# Search the movies for the title
def search_movies(query, page=1):
# query: search term
# page: page number (optional)

    if not query:
        return []
    
    url = f"{settings.TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'es-ES',
        'page': page,
        'include_adult': False
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        movies = response.json().get('results', [])
        
        # add url with the images
        for movie in movies:
            if movie.get('poster_path'):
                movie['poster_url'] = f"{settings.TMDB_IMAGE_URL}w500{movie['poster_path']}"
            if movie.get('backdrop_path'):
                movie['backdrop_url'] = f"{settings.TMDB_IMAGE_URL}original{movie['backdrop_path']}"
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"Error en TMDb API: {e}")
        return []


def get_movie_details(movie_id):
    
    url = f"{settings.TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'es-ES',
        'append_to_response': 'credits,videos,similar'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        movie = response.json()
        
        # add images url
        if movie.get('poster_path'):
            movie['poster_url'] = f"{settings.TMDB_IMAGE_URL}w500{movie['poster_path']}"
        if movie.get('backdrop_path'):
            movie['backdrop_url'] = f"{settings.TMDB_IMAGE_URL}original{movie['backdrop_path']}"
        
        # process main cast
        if 'credits' in movie:
            movie['cast'] = movie['credits'].get('cast', [])[:10]
            
            # find the director
            director = None
            for crew_member in movie['credits'].get('crew', []):
                if crew_member.get('job') == 'Director':
                    director = crew_member.get('name')
                    break
            movie['director'] = director
        
        # process the trailers
        if 'videos' in movie:
            trailers = []
            for video in movie['videos'].get('results', []):
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    trailers.append({
                        'key': video.get('key'),
                        'name': video.get('name')
                    })
            movie['trailers'] = trailers[:3]
        
        return movie
        
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo detalles de película: {e}")
        return None


def get_popular_movies(page=1):
# get the list of popular movies
    url = f"{settings.TMDB_BASE_URL}/movie/popular"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'es-ES',
        'page': page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        movies = data.get('results', [])
        
        for movie in movies:
            if movie.get('poster_path'):
                movie['poster_url'] = f"{settings.TMDB_IMAGE_URL}w342{movie['poster_path']}"
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo películas populares: {e}")
        return []


def get_now_playing_movies(page=1):
# get movies that are currently playing now in cinemas

    url = f"{settings.TMDB_BASE_URL}/movie/now_playing"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'es-ES',
        'page': page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        movies = response.json().get('results', [])
        
        for movie in movies:
            if movie.get('poster_path'):
                movie['poster_url'] = f"{settings.TMDB_IMAGE_URL}w342{movie['poster_path']}"
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo películas en cartelera: {e}")
        return []