from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BlockViewSet,
    CategoryViewSet,
    CreatorViewSet,
    DailyAnalyticsViewSet,
    DeadlineNotificationViewSet,
    FollowViewSet,
    MatchViewSet,
    MessageViewSet,
    OrderTimelineViewSet,
    OrderViewSet,
    PaymentMethodViewSet,
    ReportViewSet,
    ReviewViewSet,
    ServiceViewSet,
    SupportTicketViewSet,
    UserViewSet,
    UserWalletViewSet,
    WithdrawalViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'creators', CreatorViewSet, basename='creator')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-timeline', OrderTimelineViewSet, basename='order-timeline')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'follows', FollowViewSet, basename='follow')
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'support-tickets', SupportTicketViewSet, basename='support-ticket')
router.register(r'wallets', UserWalletViewSet, basename='wallet')
router.register(r'withdrawals', WithdrawalViewSet, basename='withdrawal')
router.register(r'deadline-notifications', DeadlineNotificationViewSet, basename='deadline-notification')
router.register(r'daily-analytics', DailyAnalyticsViewSet, basename='daily-analytics')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
]
