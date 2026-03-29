from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    MeView,
    OrderViewSet,
    ProjectViewSet,
    RegisterView,
    ServiceViewSet,
    UserViewSet,
    WalletView,
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),

    # Wallet
    path('wallet/', WalletView.as_view(), name='wallet'),

    # ViewSet routes (services, orders, projects, users)
    path('', include(router.urls)),
]
