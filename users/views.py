# IMPORTS
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Follow  # AÑADIDO Follow
from .forms import RegistroForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm
import os
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import LoginForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from movies.models import Review
from movies.tmdb_service import get_popular_movies, get_movie_details

# ***********************************************************************************+
                                        # VIEWS
# ***********************************************************************************+  

# REGISTER

def register_user(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            try:
                
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                telefono = form.cleaned_data['telefono']

             
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # El signal ya ha creado el perfil. Ahora, si el usuario introdujo un teléfono, lo guardamos.
                if telefono:
                    user.perfil.telefono = telefono
                    user.perfil.save()

                messages.success(request, "Usuario registrado correctamente")
                return redirect('users:log_in')

            except Exception as e:
                messages.error(request, f"Error al registrar: {e}")

        
        return render(request, 'users/register.html', {'form': form})

    else:
        form = RegistroForm()

    return render(request, 'users/register.html', {'form': form})

# ***********************************************************************************+

# LOG IN

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = LoginForm()
        
    return render(request, 'users/login.html', {'form': form})

# ***********************************************************************************+

# LOG OUT

@login_required
def user_logout(request):
    
    # Close sesion
    logout(request)
    
    messages.success(request, "Cerraste la sesión con anterioridad")
    return redirect('home')  # Redirige a la página principal

# ***********************************************************************************+

# USER PROFILE

@login_required
def mi_perfil(request):
    perfil = request.user.perfil
    user = request.user
    
    # Obtener las reseñas del usuario
    reseñas_usuario = Review.objects.filter(user=user).order_by('-created_at')
    
    # url of the poster of the review
    for review in reseñas_usuario:
        # if your review model has the movie_id field and you can get details from TMDB
        try:
            movie_details = get_movie_details(review.movie_id)
            if movie_details and movie_details.get('poster_path'):
                review.movie_poster = f"https://image.tmdb.org/t/p/w200{movie_details['poster_path']}"
            else:
                review.movie_poster = None
        except:
            # if none, it give you none
            review.movie_poster = None
    
    # popular movies
    peliculas_recomendadas = get_popular_movies()[:6]  # only 6
    
    return render(request, 'users/mi_perfil.html', {
        'perfil': perfil,
        'user': user,
        'reseñas_usuario': reseñas_usuario,
        'peliculas_recomendadas': peliculas_recomendadas,
    })

# ***********************************************************************************+

# PERFIL PÚBLICO DE OTROS USUARIOS

def perfil_publico(request, username):
    """Ver el perfil público de otro usuario"""
    profile_user = get_object_or_404(User, username=username)
    perfil = profile_user.perfil
    
    # Obtener las reseñas del usuario
    reseñas_usuario = Review.objects.filter(user=profile_user).order_by('-created_at')
    
    # URL del poster de las reseñas
    for review in reseñas_usuario:
        try:
            movie_details = get_movie_details(review.movie_id)
            if movie_details and movie_details.get('poster_path'):
                review.movie_poster = f"https://image.tmdb.org/t/p/w200{movie_details['poster_path']}"
            else:
                review.movie_poster = None
        except:
            review.movie_poster = None
    
    # Verificar si el usuario actual sigue a este perfil
    is_following = False
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()
    
    return render(request, 'users/perfil_publico.html', {
        'profile_user': profile_user,
        'perfil': perfil,
        'reseñas_usuario': reseñas_usuario,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

# ***********************************************************************************+

# SEGUIR USUARIO

@login_required
def follow_user(request, user_id):
    """Seguir a un usuario"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # No puedes seguirte a ti mismo
    if request.user == user_to_follow:
        messages.error(request, "No puedes seguirte a ti mismo.")
        return redirect('users:perfil_publico', username=user_to_follow.username)
    
    # Crear el follow si no existe
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        followed=user_to_follow
    )
    
    if created:
        messages.success(request, f"Ahora sigues a {user_to_follow.username}")
    else:
        messages.info(request, f"Ya sigues a {user_to_follow.username}")
    
    return redirect('users:perfil_publico', username=user_to_follow.username)

# ***********************************************************************************+

# DEJAR DE SEGUIR USUARIO

@login_required
def unfollow_user(request, user_id):
    """Dejar de seguir a un usuario"""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
    
    messages.success(request, f"Has dejado de seguir a {user_to_unfollow.username}")
    return redirect('users:perfil_publico', username=user_to_unfollow.username)

# ***********************************************************************************+

# MIS SEGUIDORES

@login_required
def mis_seguidores(request, username):
    """Ver lista de personas que siguen a un usuario específico"""
    profile_user = get_object_or_404(User, username=username)
    seguidores = profile_user.followers.all()
    return render(request, 'users/seguidores.html', {
        'seguidores': seguidores,
        'profile_user': profile_user,
    })

# ***********************************************************************************+

# MIS SIGUIENDO

@login_required
def mis_siguiendo(request, username):
    """Ver lista de personas que sigue un usuario específico"""
    profile_user = get_object_or_404(User, username=username)
    siguiendo = profile_user.following.all()
    return render(request, 'users/siguiendo.html', {
        'siguiendo': siguiendo,
        'profile_user': profile_user,
    })

# ***********************************************************************************+

# CONFIG PROFILE

@login_required
def configuracion(request):
    # get the actual user's profile
    perfil = request.user.perfil
    user = request.user
    
    if request.method == 'POST':
        # Recoger datos del formulario manual
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        avatar = request.FILES.get('avatar')
        
        # Actualizar usuario (esto cambia el nombre que aparece en el @)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Actualizar perfil
        perfil.telefono = telefono
        if avatar:
            perfil.avatar = avatar
        perfil.save()
        
        messages.success(request, "Perfil actualizado correctamente")
        return redirect('users:configuracion')
    
    return render(request, 'users/configuracion.html', {
        'perfil': perfil,
        'user': user,
    })

# ***********************************************************************************+

# DELETING ACCOUNTS

@login_required
def delete_account(request):
    user = request.user
    
    # Password verify
    password = request.POST.get('password')
    if not user.check_password(password):
        messages.error(request, 'Contraseña incorrecta. No se pudo eliminar la cuenta.')
        return redirect('users:configuracion')
    
    # Avatar existance checking and deletion
    try:
        if hasattr(user, 'perfil') and user.perfil.avatar:
            avatar_path = user.perfil.avatar.path
            if os.path.isfile(avatar_path):
                os.remove(avatar_path)
    except Exception as e:
        print(f"Error al eliminar avatar: {e}")
    
    # Close session
    logout(request)
    
    # Delete user ==== PROFILE will be destroyed too cause of CASCADE condition in PROFILE MODEL
    user.delete()
    
    messages.error(request, 'Tu cuenta ha sido eliminada permanentemente.')
    return redirect('home')

# **************************************************************************************************+

# CHANGE PASSWORD

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión para que no cierre sesión
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('users:configuracion')
        
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

# **************************************************************************************************+

# FORGOT PASSWORD RECUPERATION

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generar token y UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Crear enlace de restablecimiento
            reset_url = request.build_absolute_uri(
                reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Preparar el correo (usando texto plano para evitar problemas)
            subject = "Restablecer contrasena - Absolute Cinema"
            
            # Mensaje en texto plano (más seguro para pruebas)
            plain_message = f"""
Hola {user.username},

Haz clic en el siguiente enlace para restablecer tu contrasena:

{reset_url}

Este enlace expirara en 24 horas.

Si no solicitaste este cambio, ignora este mensaje.

--
Absolute Cinema
            """
            
            # Send email (if EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend', the message will be displayed at the console!!!!)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=None,  # Will use DEFAULT_FROM_EMAIL if it's configured
                recipient_list=[email],
                fail_silently=False,
            )
            
            
            return redirect('users:password_reset_done')
            
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con este correo electronico.')
            return redirect('users:password_reset_request')
    
    return render(request, 'users/forgot_password.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tu contrasena ha sido restablecida exitosamente.')
                return redirect('users:log_in')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        return render(request, 'users/reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'El enlace de recuperacion es invalido o ha expirado.')
        return redirect('users:password_reset_request')


def password_reset_done(request):
    return render(request, 'users/password_reset_sent.html')