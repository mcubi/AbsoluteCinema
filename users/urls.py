from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('login/', views.login_user, name='log_in'),
    path('logout', views.user_logout, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('change_password/', views.change_password, name='change_password'),
    path('', include('movies.urls')),
]