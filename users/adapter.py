from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
import uuid
from allauth.account.utils import user_email, user_username

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Se invoca justo después de que el usuario se autentica con Google.
        Aquí es donde podemos conectar la cuenta de Google a un usuario de Django existente.
        """
        user = sociallogin.user
        
        if user.email:
            try:
                existing_user = User.objects.get(email__iexact=user.email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass

    def is_auto_signup_allowed(self, request, sociallogin):
        # Permitimos el registro automático siempre.
        return True