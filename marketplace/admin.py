from django.contrib import admin

from .models import (
    AuthCredential, Block, Category, Creator, DailyAnalytics,
    DeadlineNotification, Follow, Match, Message, Order, OrderTimeline,
    PaymentMethod, Report, Review, Service, SupportTicket, User,
    UserWallet, Withdrawal,
)


@admin.register(AuthCredential)
class AuthCredentialAdmin(admin.ModelAdmin):
    list_display = ['email', 'firebase_uid', 'created_at']
    search_fields = ['email', 'firebase_uid']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'password_hash']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['firebase_uid', 'email', 'full_name', 'role', 'created_at']
    list_filter = ['role']
    search_fields = ['email', 'firebase_uid', 'first_name', 'last_name', 'full_name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'verification_status', 'experience_years', 'starting_price', 'created_at']
    list_filter = ['verification_status']
    search_fields = ['user_id']
    ordering = ['-created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['label', 'icon', 'color', 'created_at']
    ordering = ['label']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'label', 'creator_id', 'category', 'price', 'is_deleted', 'created_at']
    list_filter = ['category', 'is_deleted', 'is_public']
    search_fields = ['title', 'label', 'creator_id']
    ordering = ['-created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_title', 'client_id', 'creator_id', 'price', 'status', 'created_at']
    list_filter = ['status', 'is_deleted', 'escrow_status']
    search_fields = ['service_title', 'client_id', 'creator_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderTimeline)
class OrderTimelineAdmin(admin.ModelAdmin):
    list_display = ['order', 'event_type', 'actor_id', 'created_at']
    list_filter = ['event_type']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_id', 'reviewee_id', 'rating', 'order', 'created_at']
    list_filter = ['rating']
    ordering = ['-created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_id', 'receiver_id', 'is_read', 'is_deleted', 'created_at']
    list_filter = ['is_read', 'is_deleted']
    ordering = ['-created_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower_id', 'following_id', 'created_at']
    ordering = ['-created_at']


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['blocker_id', 'blocked_id', 'created_at']
    ordering = ['-created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter_id', 'reported_id', 'reason', 'created_at']
    ordering = ['-created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'creator_id', 'match_score', 'status', 'created_at']
    list_filter = ['status']
    ordering = ['-created_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'method_type', 'masked_number', 'created_at']
    ordering = ['-created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'user_id', 'category', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'wallet_type', 'account_name', 'is_active', 'created_at']
    list_filter = ['wallet_type', 'is_active']
    ordering = ['-created_at']


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'amount', 'status', 'method_type', 'created_at']
    list_filter = ['status']
    ordering = ['-created_at']


@admin.register(DeadlineNotification)
class DeadlineNotificationAdmin(admin.ModelAdmin):
    list_display = ['order', 'notification_type', 'sent_to', 'sent_at', 'read_at']
    ordering = ['-sent_at']


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['creator_id', 'date', 'profile_views', 'service_clicks', 'created_at']
    ordering = ['-date']
