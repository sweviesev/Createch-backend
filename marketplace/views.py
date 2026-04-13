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
# Mixin – shared query-param filtering + search
# ---------------------------------------------------------------------------

class FilterMixin:
    """
    Generic mixin: reads `filter_fields` from the view class and applies
    exact-match filters from query params.  Also supports `?search=` if
    `search_fields` is defined (case-insensitive icontains across all fields).
    """
    filter_fields: list[str] = []
    search_fields: list[str] = []

    def apply_filters(self, qs):
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value:
                qs = qs.filter(**{field: value})

        search = self.request.query_params.get('search', '').strip()
        if search and self.search_fields:
            q = db_models.Q()
            for sf in self.search_fields:
                q |= db_models.Q(**{f'{sf}__icontains': search})
            qs = qs.filter(q)

        # Optional status filter
        status_val = self.request.query_params.get('status')
        if status_val and hasattr(qs.model, 'status'):
            qs = qs.filter(status=status_val)

        return qs


# ---------------------------------------------------------------------------
# User ViewSet
# ---------------------------------------------------------------------------

class UserViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_fields = ['role']
    search_fields = ['full_name', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        return self.apply_filters(
            User.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
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

class CreatorViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = CreatorSerializer
    queryset = Creator.objects.all()
    filter_fields = ['user_id', 'verification_status']
    search_fields = ['bio', 'skills']

    def get_queryset(self):
        return self.apply_filters(
            Creator.objects.all().order_by('-created_at')
        )

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
    queryset = Category.objects.all().order_by('label')

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Service ViewSet
# ---------------------------------------------------------------------------

class ServiceViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_fields = ['creator_id', 'category']
    search_fields = ['title', 'label', 'description']

    def get_queryset(self):
        return self.apply_filters(
            Service.objects.filter(is_deleted=False).order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Order ViewSet
# ---------------------------------------------------------------------------

class OrderViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_fields = ['client_id', 'creator_id']
    search_fields = ['service_title']

    def get_queryset(self):
        return self.apply_filters(
            Order.objects.filter(is_deleted=False).order_by('-created_at')
        )

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

class OrderTimelineViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = OrderTimelineSerializer
    filter_fields = ['order_id', 'actor_id']

    def get_queryset(self):
        return self.apply_filters(
            OrderTimeline.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Review ViewSet
# ---------------------------------------------------------------------------

class ReviewViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    filter_fields = ['reviewee_id', 'reviewer_id', 'order_id']

    def get_queryset(self):
        return self.apply_filters(
            Review.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Message ViewSet
# ---------------------------------------------------------------------------

class MessageViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    search_fields = ['content']

    def get_queryset(self):
        qs = Message.objects.filter(is_deleted=False)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(
                db_models.Q(sender_id=user_id) | db_models.Q(receiver_id=user_id)
            )
        return qs.order_by('created_at')

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Follow ViewSet
# ---------------------------------------------------------------------------

class FollowViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    filter_fields = ['follower_id', 'following_id']

    def get_queryset(self):
        return self.apply_filters(
            Follow.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Block ViewSet
# ---------------------------------------------------------------------------

class BlockViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    filter_fields = ['blocker_id']

    def get_queryset(self):
        return self.apply_filters(
            Block.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Report ViewSet
# ---------------------------------------------------------------------------

class ReportViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    filter_fields = ['reporter_id', 'reported_user_id']

    def get_queryset(self):
        return self.apply_filters(
            Report.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Match ViewSet
# ---------------------------------------------------------------------------

class MatchViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    filter_fields = ['client_id', 'creator_id']

    def get_queryset(self):
        return self.apply_filters(
            Match.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# PaymentMethod ViewSet
# ---------------------------------------------------------------------------

class PaymentMethodViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    filter_fields = ['user_id']

    def get_queryset(self):
        return self.apply_filters(
            PaymentMethod.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# SupportTicket ViewSet
# ---------------------------------------------------------------------------

class SupportTicketViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    filter_fields = ['user_id', 'status', 'category', 'user_role']
    search_fields = ['message', 'email', 'ticket_number']

    def get_queryset(self):
        return self.apply_filters(
            SupportTicket.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# UserWallet ViewSet
# ---------------------------------------------------------------------------

class UserWalletViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = UserWalletSerializer
    filter_fields = ['user_id']

    def get_queryset(self):
        return self.apply_filters(
            UserWallet.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# Withdrawal ViewSet
# ---------------------------------------------------------------------------

class WithdrawalViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    filter_fields = ['user_id', 'status']

    def get_queryset(self):
        return self.apply_filters(
            Withdrawal.objects.all().order_by('-created_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# DeadlineNotification ViewSet
# ---------------------------------------------------------------------------

class DeadlineNotificationViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = DeadlineNotificationSerializer
    filter_fields = ['sent_to', 'order']

    def get_queryset(self):
        return self.apply_filters(
            DeadlineNotification.objects.all().order_by('-sent_at')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]


# ---------------------------------------------------------------------------
# DailyAnalytics ViewSet
# ---------------------------------------------------------------------------

class DailyAnalyticsViewSet(FilterMixin, viewsets.ModelViewSet):
    serializer_class = DailyAnalyticsSerializer
    filter_fields = ['creator_id']

    def get_queryset(self):
        return self.apply_filters(
            DailyAnalytics.objects.all().order_by('-date')
        )

    def get_permissions(self):
        return [permissions.AllowAny()]
