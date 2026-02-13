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
SECRET_KEY = 'django-insecure-ps_m^eet7a+*g9p$qf-%6iu56$j$qiflt3x8v12#w2*gg_%&3s'

# SECURITY WARNING: don't run with DEBUG=TRUE on in production!            <-----------------------------------------------------
DEBUG = True



ALLOWED_HOSTS = []


# APPS DEFINITION:

INSTALLED_APPS = [
    'django.contrib.admin',         # admin panel
    'django.contrib.auth',          # basic authentication
    'django.contrib.contenttypes',  # ---
    'django.contrib.sessions',      # ---
    'django.contrib.messages',      # ---
    'django.contrib.staticfiles',   # unchanging files served by us
    'movies',                       # catalog of movies and principal pages
    'users',                        # user management app
    #'prices',                      # movie prices and plans for users
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


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# DEFAULT PRIMARY KEY FIELD TYPE:
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
