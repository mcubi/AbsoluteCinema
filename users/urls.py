from django.urls import path, include
from . import views
from .api import api_register, api_login, api_logout, api_google_auth



app_name = 'users'

# NOTE: this project intentionally does NOT use django-allauth.
# Any previous references to allauth/socialaccount_login must not be used.

urlpatterns = [
    # ---------------------------
    # Vistas HTML (tus endpoints actuales)
    # ---------------------------
    path('register', views.register_user, name='register'),
    path('login/', views.login_user, name='log_in'),
    path('logout', views.user_logout, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('change_password/', views.change_password, name='change_password'),

    # Google (HTML / JSON viejo que tenías)
    path('api/auth/google/', views.google_auth, name='google_auth'),


    # ---------------------------
    # APIs JSON (lo que pediste: inicio/registro de sesión por API)
    # ---------------------------
    path('api/register', api_register, name='api_register'),
    path('api/login', api_login, name='api_login'),
    path('api/logout', api_logout, name='api_logout'),
    path('api/google-auth', api_google_auth, name='api_google_auth'),



    # Mantener rutas de movies dentro de users (si tu frontend lo usa)
    path('', include('movies.urls')),
]
