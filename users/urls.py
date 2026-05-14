from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('login/', views.login_user, name='log_in'),
    path('logout/', views.logout_user, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
]