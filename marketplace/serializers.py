from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Order, Project, Service, User, WalletTransaction


# ---------------------------------------------------------------------------
# Auth Serializers
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'middle_name', 'last_name',
            'phone', 'birth_date', 'role', 'password', 'confirm_password',
        ]
        extra_kwargs = {
            'role': {'default': 'client'},
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'middle_name', 'last_name',
            'full_name', 'phone', 'birth_date', 'role', 'status',
            'is_verified', 'reports', 'wallet_balance', 'date_joined',
        ]
        read_only_fields = ['id', 'wallet_balance', 'reports', 'date_joined', 'is_verified']


class CreatachTokenSerializer(TokenObtainPairSerializer):
    """Extends the JWT payload with role and full_name."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['email'] = user.email
        return token


# ---------------------------------------------------------------------------
# Service Serializer
# ---------------------------------------------------------------------------

class ServiceSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'creator', 'creator_name', 'title', 'description',
            'price', 'category', 'delivery_days', 'image_url',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def get_creator_name(self, obj):
        return obj.creator.full_name if obj.creator else ''

    def create(self, validated_data):
        # Automatically assign the logged-in creator
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# Order Serializer
# ---------------------------------------------------------------------------

class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField()
    creator_name = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'creator', 'service',
            'service_title', 'price', 'image_url',
            'status', 'requirements',
            'client_name', 'creator_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Auto-populate snapshot fields from the linked service
        service = validated_data.get('service')
        if service and not validated_data.get('service_title'):
            validated_data['service_title'] = service.title
        if service and not validated_data.get('price'):
            validated_data['price'] = service.price
        if service and not validated_data.get('image_url'):
            validated_data['image_url'] = service.image_url
        if service and not validated_data.get('creator'):
            validated_data['creator'] = service.creator
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class OrderStatusSerializer(serializers.ModelSerializer):
    """Lightweight serializer used only for status updates."""

    class Meta:
        model = Order
        fields = ['status']


# ---------------------------------------------------------------------------
# Project Serializer
# ---------------------------------------------------------------------------

class ProjectSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    platform_fee = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'creator', 'creator_name', 'title', 'client_name',
            'status', 'budget', 'platform_fee', 'deadline',
            'description', 'admin_note', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'creator', 'platform_fee', 'created_at', 'updated_at']

    def get_creator_name(self, obj):
        return obj.creator.full_name if obj.creator else ''

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# Wallet Serializers
# ---------------------------------------------------------------------------

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class WalletActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['deposit', 'withdraw'])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='')
