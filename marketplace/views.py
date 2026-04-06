from django.db import models as db_models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Block, Category, Creator, DailyAnalytics, DeadlineNotification,
    Follow, Match, Message, Order, OrderTimeline, PaymentMethod,
    Report, Review, Service, SupportTicket, User, UserWallet, Withdrawal,
)
from .serializers import (
    BlockSerializer,
    CategorySerializer,
    CreatorSerializer,
    DailyAnalyticsSerializer,
    DeadlineNotificationSerializer,
    FollowSerializer,
    MatchSerializer,
    MessageSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    OrderTimelineSerializer,
    PaymentMethodSerializer,
    ReportSerializer,
    ReviewSerializer,
    ServiceSerializer,
    SupportTicketSerializer,
    UserSerializer,
    UserWalletSerializer,
    WithdrawalSerializer,
)


# ---------------------------------------------------------------------------
# User ViewSet
# ---------------------------------------------------------------------------

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.AllowAny()]

    def get_object(self):
        """Allow lookup by firebase_uid as well as pk."""
        lookup = self.kwargs.get(self.lookup_field)
        try:
            return User.objects.get(pk=lookup)
        except (User.DoesNotExist, ValueError):
            return User.objects.get(firebase_uid=lookup)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Admin action to suspend a user (set role to a suspended state)."""
        user = self.get_object()
        return Response({'message': f'User {user.email} suspend action received.'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Admin action to activate a user."""
        user = self.get_object()
        return Response({'message': f'User {user.email} activate action received.'})


# ---------------------------------------------------------------------------
# Creator ViewSet
# ---------------------------------------------------------------------------

class CreatorViewSet(viewsets.ModelViewSet):
    serializer_class = CreatorSerializer
    queryset = Creator.objects.all()

    def get_permissions(self):
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'], url_path='by-uid/(?P<uid>[^/.]+)')
    def by_uid(self, request, uid=None):
        """GET /api/creators/by-uid/<firebase_uid>/"""
        try:
            creator = Creator.objects.get(user_id=uid)
            return Response(CreatorSerializer(creator).data)
        except Creator.DoesNotExist:
            return Response({'detail': 'Creator not found.'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Category ViewSet
# ---------------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Service ViewSet
# ---------------------------------------------------------------------------

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        qs = Service.objects.filter(is_deleted=False)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Order ViewSet
# ---------------------------------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.filter(is_deleted=False)
        client_id = self.request.query_params.get('client_id')
        creator_id = self.request.query_params.get('creator_id')
        if client_id:
            qs = qs.filter(client_id=client_id)
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'], url_path='update_status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Status updated.', 'status': serializer.data['status']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# OrderTimeline ViewSet
# ---------------------------------------------------------------------------

class OrderTimelineViewSet(viewsets.ModelViewSet):
    serializer_class = OrderTimelineSerializer

    def get_queryset(self):
        qs = OrderTimeline.objects.all()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Review ViewSet
# ---------------------------------------------------------------------------

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        qs = Review.objects.all()
        reviewee_id = self.request.query_params.get('reviewee_id')
        if reviewee_id:
            qs = qs.filter(reviewee_id=reviewee_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Message ViewSet
# ---------------------------------------------------------------------------

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        qs = Message.objects.filter(is_deleted=False)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(
                db_models.Q(sender_id=user_id) | db_models.Q(receiver_id=user_id)
            )
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Follow ViewSet
# ---------------------------------------------------------------------------

class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        qs = Follow.objects.all()
        follower_id = self.request.query_params.get('follower_id')
        following_id = self.request.query_params.get('following_id')
        if follower_id:
            qs = qs.filter(follower_id=follower_id)
        if following_id:
            qs = qs.filter(following_id=following_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Block ViewSet
# ---------------------------------------------------------------------------

class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer

    def get_queryset(self):
        qs = Block.objects.all()
        blocker_id = self.request.query_params.get('blocker_id')
        if blocker_id:
            qs = qs.filter(blocker_id=blocker_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Report ViewSet
# ---------------------------------------------------------------------------

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Match ViewSet
# ---------------------------------------------------------------------------

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer

    def get_queryset(self):
        qs = Match.objects.all()
        client_id = self.request.query_params.get('client_id')
        creator_id = self.request.query_params.get('creator_id')
        if client_id:
            qs = qs.filter(client_id=client_id)
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# PaymentMethod ViewSet
# ---------------------------------------------------------------------------

class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer

    def get_queryset(self):
        qs = PaymentMethod.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# SupportTicket ViewSet
# ---------------------------------------------------------------------------

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer

    def get_queryset(self):
        qs = SupportTicket.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# UserWallet ViewSet
# ---------------------------------------------------------------------------

class UserWalletViewSet(viewsets.ModelViewSet):
    serializer_class = UserWalletSerializer

    def get_queryset(self):
        qs = UserWallet.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Withdrawal ViewSet
# ---------------------------------------------------------------------------

class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer

    def get_queryset(self):
        qs = Withdrawal.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# DeadlineNotification ViewSet
# ---------------------------------------------------------------------------

class DeadlineNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = DeadlineNotificationSerializer
    queryset = DeadlineNotification.objects.all()

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# DailyAnalytics ViewSet
# ---------------------------------------------------------------------------

class DailyAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = DailyAnalyticsSerializer

    def get_queryset(self):
        qs = DailyAnalytics.objects.all()
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return qs

    def get_permissions(self):
        return [permissions.AllowAny()]
