"""
Authentication views: Register, Login, Me.
Uses PyJWT for token generation and Django's password hashers for security.
"""

import uuid as _uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .models import AuthCredential, Creator, User
from .serializers import UserSerializer


# ── helpers ────────────────────────────────────────────────────────────────

def _generate_token(firebase_uid: str, email: str) -> str:
    """Create a signed JWT valid for 24 hours."""
    payload = {
        'firebase_uid': firebase_uid,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


# ── Register ───────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Creates a new user account with hashed password and returns a JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        confirm_password = request.data.get('confirm_password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        phone = request.data.get('phone', '').strip()
        role = request.data.get('role', 'client')

        # ── validation ─────────────────────────────────────────────────
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != confirm_password:
            return Response(
                {'error': 'Passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if AuthCredential.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered.'},
                status=status.HTTP_409_CONFLICT,
            )

        # ── create user + credential ───────────────────────────────────
        firebase_uid = f'django_{_uuid.uuid4().hex[:16]}'
        full_name = f'{first_name} {last_name}'.strip()

        user = User.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name or email,
            phone=phone,
            role=role,
        )

        AuthCredential.objects.create(
            firebase_uid=firebase_uid,
            email=email,
            password_hash=make_password(password),
        )

        # auto-create creator profile when role is creator
        if role == 'creator':
            Creator.objects.create(user_id=firebase_uid)

        token = _generate_token(firebase_uid, email)

        return Response(
            {
                'message': 'Registration successful.',
                'access': token,
                'firebase_uid': firebase_uid,
                'email': email,
                'role': role,
                'full_name': full_name,
            },
            status=status.HTTP_201_CREATED,
        )


# ── Login ──────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates with email + password and returns a JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cred = AuthCredential.objects.get(email=email)
        except AuthCredential.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, cred.password_hash):
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(firebase_uid=cred.firebase_uid)
        except User.DoesNotExist:
            return Response(
                {'error': 'User profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = _generate_token(cred.firebase_uid, email)

        return Response({
            'message': 'Login successful.',
            'access': token,
            'firebase_uid': cred.firebase_uid,
            'email': email,
            'role': user.role,
            'full_name': user.full_name,
        })


# ── Me (profile) ──────────────────────────────────────────────────────────

class MeView(APIView):
    """
    GET /api/auth/me/
    Returns the profile of the currently authenticated user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
