from rest_framework import serializers

from .models import (
    Block, Category, Creator, DailyAnalytics, DeadlineNotification,
    Follow, Match, Message, Order, OrderTimeline, PaymentMethod,
    Report, Review, Service, SupportTicket, User, UserWallet, Withdrawal,
)


# ---------------------------------------------------------------------------
# User Serializers
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'firebase_uid', 'email', 'first_name', 'middle_name',
            'last_name', 'full_name', 'display_name', 'avatar_url', 'phone',
            'birthdate', 'age', 'gender', 'nationality', 'address', 'role',
            'language', 'notifications_enabled', 'id_number', 'id_document_url',
            'id_front_url', 'id_back_url', 'id_selfie_url',
            'street_address', 'barangay', 'city', 'province',
            'postal_code', 'country', 'created_at',
            'notifications_updated_at', 'orders_last_seen_at',
            'follows_last_seen_at',
        ]
        read_only_fields = ['id', 'created_at']


class UserMinimalSerializer(serializers.ModelSerializer):
    """Lightweight serializer for embedding user info in other responses."""
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['firebase_uid', 'email', 'full_name', 'display_name', 'avatar_url', 'role']


# ---------------------------------------------------------------------------
# Creator Serializer
# ---------------------------------------------------------------------------

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = [
            'id', 'user_id', 'bio', 'skills', 'portfolio_url',
            'experience_years', 'starting_price', 'turnaround_time',
            'custom_skills', 'verification_status', 'response_time',
            'cover_url', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Category Serializer
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'label', 'icon', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Service Serializer
# ---------------------------------------------------------------------------

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'creator_id', 'title', 'label', 'description',
            'price', 'category', 'icon', 'image_url', 'is_public',
            'target_client_id', 'is_deleted', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Order Serializers
# ---------------------------------------------------------------------------

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'client_id', 'creator_id', 'service_title', 'price',
            'status', 'client_name', 'creator_name', 'image_url',
            'last_updated_by', 'preview_url', 'final_file_url',
            'delivery_url', 'delivery_note',
            'payment_method_used', 'payout_method_snapshot',
            'escrow_status', 'escrow_amount',
            'due_date', 'deadline_extension_days',
            'deadline_extension_requested_at',
            'deadline_extension_approved', 'deadline_extension_reason',
            'auto_deadline_notification_sent', 'deadline_passed',
            'estimated_completion_days', 'work_started_at',
            'refund_requested_at', 'refund_approved',
            'refund_responded_at', 'refund_reason',
            'rating', 'review_comment', 'reviewed_at',
            'is_deleted', 'deleted_at', 'deleted_by',
            'deleted_by_client', 'deleted_by_creator',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderStatusSerializer(serializers.ModelSerializer):
    """Lightweight serializer used only for status updates."""

    class Meta:
        model = Order
        fields = ['status']


# ---------------------------------------------------------------------------
# OrderTimeline Serializer
# ---------------------------------------------------------------------------

class OrderTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTimeline
        fields = [
            'id', 'order', 'event_type', 'actor_id',
            'message', 'metadata', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Review Serializer
# ---------------------------------------------------------------------------

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'order', 'reviewer_id', 'reviewee_id',
            'rating', 'comment', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Message Serializer
# ---------------------------------------------------------------------------

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'sender_id', 'receiver_id', 'content',
            'is_read', 'media_url', 'is_deleted', 'service_data',
            'from_smart_match', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Follow Serializer
# ---------------------------------------------------------------------------

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower_id', 'following_id', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Block Serializer
# ---------------------------------------------------------------------------

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'blocker_id', 'blocked_id', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Report Serializer
# ---------------------------------------------------------------------------

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'reporter_id', 'reported_id', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Match Serializer
# ---------------------------------------------------------------------------

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id', 'client_id', 'creator_id', 'match_score',
            'project_description', 'reasons', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# PaymentMethod Serializer
# ---------------------------------------------------------------------------

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'user_id', 'method_type', 'masked_number', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# SupportTicket Serializer
# ---------------------------------------------------------------------------

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user_id', 'email', 'category',
            'message', 'status', 'priority', 'user_role', 'user_info',
            'admin_response', 'resolved_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ---------------------------------------------------------------------------
# UserWallet Serializer
# ---------------------------------------------------------------------------

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ['id', 'user_id', 'wallet_type', 'account_name', 'account_number', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# Withdrawal Serializer
# ---------------------------------------------------------------------------

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'user_id', 'amount', 'status', 'method_type', 'account_details', 'created_at']
        read_only_fields = ['id', 'created_at']


# ---------------------------------------------------------------------------
# DeadlineNotification Serializer
# ---------------------------------------------------------------------------

class DeadlineNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadlineNotification
        fields = ['id', 'order', 'notification_type', 'sent_to', 'sent_at', 'read_at']
        read_only_fields = ['id', 'sent_at']


# ---------------------------------------------------------------------------
# DailyAnalytics Serializer
# ---------------------------------------------------------------------------

class DailyAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAnalytics
        fields = ['id', 'creator_id', 'date', 'profile_views', 'service_clicks', 'created_at']
        read_only_fields = ['id', 'created_at']
