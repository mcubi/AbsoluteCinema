# AbsoluteCinema

A Netflix-style audiovisual review platform, developed as a Final Degree Project (TFG). The app allows users to explore movie and series catalogs, and post reviews of them so other people can talk about the film / serie, and provide extra information for who is interested on it.

## Features

### Content Exploration

- **Full catalog**: Browse movies and series with detailed information
- **Advanced search**: Search by title, genre, year, and more
- **Interface preferences**: Customize the user experience

### User Management

- **Registration & authentication**: Traditional registration and social authentication
- **Google login**: OAuth 2.0 integration via django-allauth
- **Personal space**: Private user area with personal data and settings
- **Favorites list**: Personal board to save favorite content
- **Profile customization**: Avatar and preferences management
- **Following system**: People can follow those whose reviews they find interesting

### Security

- **Google authentication**: Secure login via OAuth 2.0
- **Password validation**: Robust validation system
- **CSRF protection**: Integrated security middleware
- **Session management**: Secure user session control

## Tech Stack

### Backend

- **Python 3**: Main programming language
- **Django 5.2.7**: Web framework for rapid development
- **Django Channels 4.0**: WebSocket support for real-time features
- **Django REST Framework**: REST API for web services
- **django-allauth**: Social authentication (Google OAuth)
- **SQLite**: Lightweight database (development only)
- **Redis 5.0**: Cache and channel layer for WebSockets
- **Daphne 4.2**: ASGI server for Django Channels

### Frontend

- **HTML5/CSS3**: Base structure and styles
- **Tailwind CSS**: CSS utility framework
- **django-tailwind**: Tailwind integration with Django
- **JavaScript**: Client-side interactivity
- **WebSocket**: Real-time communication for the chatbot

### External APIs

- **TMDB API**: The Movie Database for movies and series info
- **Google OAuth API**: Social authentication

### DevOps

- **Docker**: Application containerization
- **Docker Compose**: Service orchestration (web + redis)
- **Pipenv**: Dependency and virtual environment management

## Installation Guide

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.10+

#### 1. Clone the repository

```
git clone <repository-url>
cd AbsoluteCinema-main
```

#### 2. Configure environment variables

Create a .env file in the project root:

```
SECRET_KEY=django-insecure-your-secret-key-here
TMDB_API_KEY=your-tmdb-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8142
```

- TMDB API Key: Register at themoviedb.org and create an application

- Google OAuth: Create a project in Google Cloud Console, enable Google+ API, and configure OAuth 2.0 credentials

#### 3. Build and run with Docker Compose

```
docker compose up --build
```

- The application will be available at: http://localhost:8142

#### 4. Run database migrations (first time only)

```
docker compose exec web python manage.py migrate
```

#### 5. (Optional) Create a superuser for admin panel

```
docker compose exec web python manage.py createsuperuser
```

#### 6. Useful Docker Commands

# Stop containers

docker compose down

# View logs

docker compose logs -f

# Run any Django command

docker compose exec web python manage.py <command>

# Rebuild without cache

docker compose build --no-cache

# Stop and remove containers + volumes (deletes database)

docker compose down -v

## Project structure:

ABSOLUTECINEMA/
├── absolute_cinema/ # Main project config
│ ├── **init**.py
│ ├── asgi.py # ASGI config for WebSockets
│ ├── settings.py # Django settings
│ ├── urls.py # Main URLs
│ └── wsgi.py # WSGI config
├── movies/ # Movie catalog app
│ ├── consumers.py # WebSocket consumers (chatbot)
│ ├── models.py # Movie data models
│ ├── tmdb_service.py # TMDB API integration
│ ├── views.py # Catalog views
│ ├── urls.py # Movie URLs
│ ├── templates/ # Movie HTML templates
│ └── migrations/ # Database migrations
├── users/ # User management app
│ ├── adapter.py # Custom allauth adapter
│ ├── forms.py # User forms
│ ├── models.py # Extended user models
│ ├── views.py # Auth and profile views
│ ├── urls.py # User URLs
│ ├── templates/ # User HTML templates
│ └── migrations/ # Database migrations
├── static/ # Static files (CSS, JS, images)
├── templates/ # Global base templates
├── media/ # User-uploaded files
├── manage.py # Django management script
├── requirements.txt # Python dependencies
├── Pipfile # Pipenv configuration
├── .env # Environment variables (not versioned)
├── dockerfile # Docker configuration
├── compose.yml # Docker Compose configuration
└── db.sqlite3 # SQLite database (development)

## License

This project is developed as a Final Degree Project (TFG). Contact the author for license information.

## Contact

For questions or support, contact the main developer.

#### Last updated: May 2026
