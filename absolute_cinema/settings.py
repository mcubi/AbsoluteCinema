"""
SETTINGS:

DJANGO 5.2.7 DOCUMENTATION:
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""



# IMPORTS:

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with DEBUG=TRUE on in production!            <-----------------------------------------------------
DEBUG = True



ALLOWED_HOSTS = []


# APPS DEFINITION:

INSTALLED_APPS = [
    'daphne',                       #---
    'django.contrib.admin',         # admin panel
    'django.contrib.auth',          # basic authentication
    'django.contrib.contenttypes',  # ---
    'django.contrib.sessions',      # ---
    'django.contrib.sites',         # required by allauth
    'django.contrib.messages',      # ---
    'django.contrib.staticfiles',   # unchanging files served by us
    'movies',                       # catalog of movies and principal pages
    'users',                        # user management app
    'channels',                     # websocket channel layer support
    
    # allauth apps for google authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # specific provider
]

# MIDDLEWARES:

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # allauth middleware
]

ROOT_URLCONF = 'absolute_cinema.urls'


# HTML FILE LOCATION:

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI DECLARATION:

WSGI_APPLICATION = 'absolute_cinema.wsgi.application'


# CHANNEL LAYERS FOR WEBSOCKET PROTOCOL:

ASGI_APPLICATION = 'absolute_cinema.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)], # Apunta al contenedor 'redis' de Docker
            
        },
    },
}

# CACHÉ CON REDIS
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/1", # Usamos la base de datos 1 para no pisar a los WebSockets (que usan la 0)
       
    }
}



# DATABASE:
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# PASSOWRD VALIDATION:
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# INTERNATIONALIZATION:
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# UNCHANGING FILES SERVED BY US (CSS, JavaScript, Images):
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# DEFAULT PRIMARY KEY FIELD TYPE:
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CONFIGURATION OF THE API (TMDb)

# API Key of the movie database (TMDb)
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# URLs base para TMDb
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/'

# verify that the key was loaded correctly (for debugging)
if not TMDB_API_KEY:
    print("ADVERTENCIA: TMDB_API_KEY no encontrada en el archivo .env")
    
# for profile images
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================
# ALLAUTH CONFIGURATION

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Le decimos a Django cuál es nuestra página de inicio de sesión personalizada
LOGIN_URL = 'users:log_in'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # Cargamos las credenciales desde el archivo .env
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': '' # Dejar vacío
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'VERIFIED_EMAIL': True,
    }
}

# Para que el registro con Google sea automático y no pida confirmación
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Le decimos a allauth que use nuestro adaptador personalizado para cuentas sociales.
SOCIALACCOUNT_ADAPTER = 'users.adapter.MySocialAccountAdapter'


# E-MAIL CONFIGURATION (ft. password recuperation)

# test_phase (eliminate in production case, replace with @real config commented below)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# real config:
# EMAIL_HOST = #SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your_correo@gmail.com'
# EMAIL_HOST_PASSWORD = 'your password'

# codification:
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# language (spanish)
LANGUAGE_CODE = 'es-es'
USE_I18N = True
USE_L10N = True