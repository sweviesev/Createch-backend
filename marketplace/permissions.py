"""
Custom RBAC permission classes for CREATECH.
Enforces role-based access control at the API level.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Only allow users with role='admin'."""

    def has_permission(self, request, view):
        return (
            request.user
            and getattr(request.user, 'is_authenticated', False)
            and getattr(request.user, 'role', None) == 'admin'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access if the requesting user owns the resource or is an admin.
    Ownership is determined by matching `firebase_uid` against common
    owner fields on the object (user_id, client_id, creator_id, sender_id,
    receiver_id, reporter_id, follower_id, blocker_id, reviewer_id, sent_to).
    """

    # Fields that can indicate ownership on different models
    OWNER_FIELDS = (
        'firebase_uid',   # User model
        'user_id',        # Creator, PaymentMethod, Wallet, Withdrawal, SupportTicket
        'client_id',      # Order, Match
        'creator_id',     # Order, Service, Match, DailyAnalytics
        'sender_id',      # Message
        'receiver_id',    # Message
        'reporter_id',    # Report
        'follower_id',    # Follow
        'following_id',   # Follow
        'blocker_id',     # Block
        'reviewer_id',    # Review
        'reviewee_id',    # Review
        'sent_to',        # DeadlineNotification
        'actor_id',       # OrderTimeline
    )

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'admin':
            return True

        uid = getattr(request.user, 'firebase_uid', None)
        if not uid:
            return False

        for field in self.OWNER_FIELDS:
            value = getattr(obj, field, None)
            if value and value == uid:
                return True

        return False


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to unauthenticated users.
    Write operations require authentication.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user
            and getattr(request.user, 'is_authenticated', False)
        )
