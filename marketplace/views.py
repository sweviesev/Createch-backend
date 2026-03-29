from decimal import Decimal

from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Order, Project, Service, User, WalletTransaction
from .serializers import (
    CreatachTokenSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    ProjectSerializer,
    RegisterSerializer,
    ServiceSerializer,
    UserSerializer,
    WalletActionSerializer,
    WalletTransactionSerializer,
)


# ---------------------------------------------------------------------------
# Permissions helpers
# ---------------------------------------------------------------------------

class IsCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'creator'


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    """POST /api/auth/register/ — public, no auth required."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'Account created successfully. Please verify your email.',
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — returns access + refresh JWT tokens."""
    permission_classes = [permissions.AllowAny]
    serializer_class = CreatachTokenSerializer


class MeView(APIView):
    """GET /api/auth/me/ — returns the current user's profile."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Service ViewSet
# ---------------------------------------------------------------------------

class ServiceViewSet(viewsets.ModelViewSet):
    """
    GET    /api/services/         — list all active services
    POST   /api/services/         — create (creator only)
    GET    /api/services/{id}/    — retrieve
    PATCH  /api/services/{id}/    — update (owner or admin)
    DELETE /api/services/{id}/    — delete (owner or admin)
    """
    serializer_class = ServiceSerializer

    def get_queryset(self):
        qs = Service.objects.select_related('creator').filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsCreator()]

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        if request.user != service.creator and request.user.role != 'admin':
            return Response(
                {'detail': 'You do not have permission to delete this service.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        service.is_active = False
        service.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Order ViewSet
# ---------------------------------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    """
    GET    /api/orders/                      — list (filtered by user role)
    POST   /api/orders/                      — place an order (client)
    GET    /api/orders/{id}/                 — retrieve
    POST   /api/orders/{id}/update_status/   — change status
    """
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Order.objects.filter(client=user).select_related('client', 'creator', 'service')
        elif user.role == 'creator':
            return Order.objects.filter(creator=user).select_related('client', 'creator', 'service')
        # Admin sees all
        return Order.objects.all().select_related('client', 'creator', 'service')

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='update_status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Status updated.', 'status': serializer.data['status']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Project ViewSet
# ---------------------------------------------------------------------------

class ProjectViewSet(viewsets.ModelViewSet):
    """
    GET    /api/projects/                  — list
    POST   /api/projects/                  — create
    GET    /api/projects/{id}/             — retrieve
    PATCH  /api/projects/{id}/             — update
    DELETE /api/projects/{id}/             — delete
    POST   /api/projects/{id}/suspend/     — admin force-suspend
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.select_related('creator')
        if user.role == 'creator':
            return qs.filter(creator=user)
        # Clients and admins see all
        return qs.all()

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user != project.creator and request.user.role != 'admin':
            return Response(
                {'detail': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)
        project = self.get_object()
        project.status = 'Suspended'
        project.admin_note = request.data.get('admin_note', 'Force suspended by Administrator.')
        project.save()
        return Response(ProjectSerializer(project).data)


# ---------------------------------------------------------------------------
# Wallet View
# ---------------------------------------------------------------------------

class WalletView(APIView):
    """
    GET  /api/wallet/  — balance + recent transactions
    POST /api/wallet/  — deposit or withdraw
    """

    def get(self, request):
        transactions = WalletTransaction.objects.filter(user=request.user)[:20]
        return Response({
            'balance': str(request.user.wallet_balance),
            'transactions': WalletTransactionSerializer(transactions, many=True).data,
        })

    def post(self, request):
        serializer = WalletActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data['action']
        amount = Decimal(str(serializer.validated_data['amount']))
        description = serializer.validated_data.get('description', '')
        user = request.user

        with transaction.atomic():
            u = User.objects.select_for_update().get(pk=user.pk)
            if action_type == 'withdraw':
                if u.wallet_balance < amount:
                    return Response(
                        {'detail': 'Insufficient funds.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                u.wallet_balance -= amount
                tx_type = 'withdrawal'
            else:
                u.wallet_balance += amount
                tx_type = 'deposit'
            u.save()

            tx = WalletTransaction.objects.create(
                user=u,
                transaction_type=tx_type,
                amount=amount,
                description=description or f'{tx_type.capitalize()} of ₱{amount}',
            )

        return Response(
            {
                'message': f'₱{amount} {tx_type} successful.',
                'new_balance': str(u.wallet_balance),
                'transaction': WalletTransactionSerializer(tx).data,
            }
        )


# ---------------------------------------------------------------------------
# Users ViewSet  (admin panel use)
# ---------------------------------------------------------------------------

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/users/       — admin: list all users
    GET /api/users/{id}/  — admin: retrieve user
    POST /api/users/{id}/suspend/ — admin: suspend a user
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsAdminRole()]

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        user = self.get_object()
        user.status = 'Suspended'
        user.save()
        return Response({'message': f'User {user.email} has been suspended.'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.status = 'Active'
        user.save()
        return Response({'message': f'User {user.email} has been activated.'})
