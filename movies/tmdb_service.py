import requests
import random
from django.conf import settings

# Settings API TMDb
API_KEY = settings.TMDB_API_KEY
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page=1"
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
    url = f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&language=es-ES&page=1"
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
    url = f"{BASE_URL}/movie/top_rated?api_key={API_KEY}&language=es-ES&page=1"
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


def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # for the cast
        cast = []
        if 'credits' in data and 'cast' in data['credits']:
            for actor in data['credits']['cast'][:12]:
                cast.append({
                    'name': actor.get('name'),
                    'character': actor.get('character'),
                    'profile_path': actor.get('profile_path'),
                })
        
        # for the director
        director = None
        if 'credits' in data and 'crew' in data['credits']:
            for crew_member in data['credits']['crew']:
                if crew_member.get('job') == 'Director':
                    director = crew_member.get('name')
                    break
        
        # genres
        genres = []
        if 'genres' in data:
            for genre in data['genres']:
                genres.append({
                    'id': genre.get('id'),
                    'name': genre.get('name'),
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
    return all_movies[:limit]