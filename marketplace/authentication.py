"""
Custom JWT authentication for Django REST Framework.
Verifies Bearer tokens and resolves the marketplace User by firebase_uid.
"""

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that reads a JWT from the Authorization header,
    decodes it, and returns the matching marketplace User instance.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

        try:
            user = User.objects.get(firebase_uid=payload['firebase_uid'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found.')

        return (user, token)
