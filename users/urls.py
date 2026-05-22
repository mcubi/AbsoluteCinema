from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('login/', views.login_user, name='log_in'),
    path('logout', views.user_logout, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'), 
    path('configuracion/', views.configuracion, name='configuracion'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('change_password/', views.change_password, name='change_password'),
    path('reset-password/done/', views.password_reset_done, name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('forgot-password/', views.password_reset_request, name='password_reset_request'),
    path('seguir/<int:user_id>/', views.follow_user, name='follow'),
    path('dejar-de-seguir/<int:user_id>/', views.unfollow_user, name='unfollow'),
    path('seguidores/<str:username>/', views.mis_seguidores, name='seguidores'),
    path('siguiendo/<str:username>/', views.mis_siguiendo, name='siguiendo'),
    path('', include('movies.urls')),
]