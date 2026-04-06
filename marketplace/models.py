import uuid as _uuid

from django.db import models


# ---------------------------------------------------------------------------
# User  (maps to Supabase "users" table — Firebase Auth backed)
# ---------------------------------------------------------------------------
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=_uuid.uuid4, editable=False)
    firebase_uid = models.TextField(unique=True)
    email = models.TextField(blank=True, null=True)
    full_name = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    middle_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    birthdate = models.TextField(blank=True, null=True)
    age = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    nationality = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.TextField(default='client', blank=True, null=True)
    language = models.TextField(default='English', blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True, null=True)

    # ID verification fields
    id_number = models.TextField(blank=True, null=True)
    id_document_url = models.TextField(blank=True, null=True)
    id_front_url = models.TextField(blank=True, null=True)
    id_back_url = models.TextField(blank=True, null=True)
    id_selfie_url = models.TextField(blank=True, null=True)

    # Address breakdown
    street_address = models.TextField(blank=True, null=True)
    barangay = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    province = models.TextField(blank=True, null=True)
    postal_code = models.TextField(blank=True, null=True)
    country = models.TextField(default='Philippines', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    notifications_updated_at = models.DateTimeField(null=True, blank=True)
    orders_last_seen_at = models.DateTimeField(null=True, blank=True)
    follows_last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name or self.email} ({self.firebase_uid})'

    @property
    def display_name(self):
        if self.full_name:
            return self.full_name
        parts = [p for p in [self.first_name, self.last_name] if p]
        return ' '.join(parts) if parts else (self.email or self.firebase_uid)


# ---------------------------------------------------------------------------
# Creator  (extended profile for creator users)
# ---------------------------------------------------------------------------
class Creator(models.Model):
    user_id = models.TextField()  # references users.firebase_uid
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)  # _text array stored as text
    portfolio_url = models.TextField(blank=True, null=True)
    experience_years = models.TextField(blank=True, null=True)
    starting_price = models.TextField(blank=True, null=True)
    turnaround_time = models.TextField(blank=True, null=True)
    custom_skills = models.JSONField(default=list, blank=True, null=True)
    verification_status = models.TextField(default='unverified', blank=True, null=True)
    response_time = models.TextField(blank=True, null=True)
    cover_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'creators'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Creator profile: {self.user_id}'


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
class Category(models.Model):
    label = models.TextField()
    icon = models.TextField()
    color = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'categories'
        managed = False
        verbose_name_plural = 'Categories'
        ordering = ['label']

    def __str__(self):
        return self.label


# ---------------------------------------------------------------------------
# Service  (offered by a Creator)
# ---------------------------------------------------------------------------
class Service(models.Model):
    creator_id = models.TextField(blank=True, null=True)  # references users.firebase_uid
    title = models.TextField(blank=True, null=True)
    label = models.TextField()
    description = models.TextField(blank=True, null=True)
    price = models.TextField(default='Negotiable', blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    icon = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True, null=True)
    target_client_id = models.TextField(blank=True, null=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.TextField(blank=True, null=True)
    deleted_by_client = models.TextField(blank=True, null=True)
    deleted_by_creator = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'services'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title or self.label} (creator: {self.creator_id})'


# ---------------------------------------------------------------------------
# Order  (client places an order for a creator's service)
# ---------------------------------------------------------------------------
class Order(models.Model):
    client_id = models.TextField()  # references users.firebase_uid
    creator_id = models.TextField()  # references users.firebase_uid
    service_title = models.TextField()
    price = models.TextField(default='Negotiable', blank=True, null=True)
    status = models.TextField(default='pending', blank=True, null=True)
    client_name = models.TextField(blank=True, null=True)
    creator_name = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    last_updated_by = models.TextField(blank=True, null=True)

    # Delivery
    preview_url = models.TextField(blank=True, null=True)
    final_file_url = models.TextField(blank=True, null=True)
    delivery_url = models.TextField(blank=True, null=True)
    delivery_note = models.TextField(blank=True, null=True)

    # Payment
    payment_method_used = models.TextField(blank=True, null=True)
    payout_method_snapshot = models.TextField(blank=True, null=True)
    escrow_status = models.TextField(default='pending', blank=True, null=True)
    escrow_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Deadlines
    due_date = models.DateTimeField(null=True, blank=True)
    deadline_extension_days = models.IntegerField(default=0, null=True, blank=True)
    deadline_extension_requested_at = models.DateTimeField(null=True, blank=True)
    deadline_extension_approved = models.BooleanField(default=False, null=True)
    deadline_extension_reason = models.TextField(blank=True, null=True)
    auto_deadline_notification_sent = models.BooleanField(default=False, null=True)
    deadline_passed = models.BooleanField(default=False, null=True)
    estimated_completion_days = models.IntegerField(null=True, blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)

    # Refund
    refund_requested_at = models.DateTimeField(null=True, blank=True)
    refund_approved = models.BooleanField(default=False, null=True)
    refund_responded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True, null=True)

    # Review
    rating = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    review_comment = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.TextField(blank=True, null=True)
    deleted_by_client = models.TextField(blank=True, null=True)
    deleted_by_creator = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'orders'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.service_title} ({self.client_name or self.client_id})'


# ---------------------------------------------------------------------------
# OrderTimeline  (event log for an order)
# ---------------------------------------------------------------------------
class OrderTimeline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline', db_column='order_id')
    event_type = models.TextField()
    actor_id = models.TextField()  # references users.firebase_uid
    message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'order_timeline'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} on Order #{self.order_id}'


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------
class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', db_column='order_id')
    reviewer_id = models.TextField()  # references users.firebase_uid
    reviewee_id = models.TextField()  # references users.firebase_uid
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'reviews'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Review by {self.reviewer_id} for {self.reviewee_id} — {self.rating}★'


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------
class Message(models.Model):
    sender_id = models.TextField()  # references users.firebase_uid
    receiver_id = models.TextField()  # references users.firebase_uid
    content = models.TextField()
    is_read = models.BooleanField(default=False, null=True)
    media_url = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    service_data = models.JSONField(null=True, blank=True)
    from_smart_match = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'messages'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Message from {self.sender_id} to {self.receiver_id}'


# ---------------------------------------------------------------------------
# Follow
# ---------------------------------------------------------------------------
class Follow(models.Model):
    follower_id = models.TextField()  # references users.firebase_uid
    following_id = models.TextField()  # references users.firebase_uid
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'follows'
        managed = False
        unique_together = ('follower_id', 'following_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower_id} follows {self.following_id}'


# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------
class Block(models.Model):
    blocker_id = models.TextField()  # references users.firebase_uid
    blocked_id = models.TextField()  # references users.firebase_uid
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'blocks'
        managed = False
        unique_together = ('blocker_id', 'blocked_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.blocker_id} blocked {self.blocked_id}'


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
class Report(models.Model):
    reporter_id = models.TextField()  # references users.firebase_uid
    reported_id = models.TextField()  # references users.firebase_uid
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'reports'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Report by {self.reporter_id} against {self.reported_id}'


# ---------------------------------------------------------------------------
# Match  (smart matching between client and creator)
# ---------------------------------------------------------------------------
class Match(models.Model):
    client_id = models.TextField()  # references users.firebase_uid
    creator_id = models.TextField()  # references users.firebase_uid
    match_score = models.IntegerField(null=True, blank=True)
    project_description = models.TextField(blank=True, null=True)
    reasons = models.JSONField(default=list, blank=True, null=True)
    status = models.TextField(default='new', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'matches'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Match: {self.client_id} ↔ {self.creator_id} (score: {self.match_score})'


# ---------------------------------------------------------------------------
# PaymentMethod
# ---------------------------------------------------------------------------
class PaymentMethod(models.Model):
    user_id = models.TextField()  # references users.firebase_uid
    method_type = models.TextField()
    masked_number = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'payment_methods'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.method_type} •••{self.masked_number} ({self.user_id})'


# ---------------------------------------------------------------------------
# SupportTicket
# ---------------------------------------------------------------------------
class SupportTicket(models.Model):
    ticket_number = models.TextField(unique=True)
    user_id = models.TextField()  # references users.firebase_uid
    email = models.TextField()
    category = models.TextField(blank=True, null=True)
    message = models.TextField()
    status = models.TextField(default='open', blank=True, null=True)
    priority = models.TextField(default='normal', blank=True, null=True)
    user_role = models.TextField(blank=True, null=True)
    user_info = models.JSONField(null=True, blank=True)
    admin_response = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'support_tickets'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Ticket {self.ticket_number} — {self.status}'


# ---------------------------------------------------------------------------
# UserWallet  (payout method for creators)
# ---------------------------------------------------------------------------
class UserWallet(models.Model):
    user_id = models.TextField()  # references users.firebase_uid
    wallet_type = models.TextField()
    account_name = models.TextField()
    account_number = models.TextField()
    is_active = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'user_wallets'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.wallet_type} — {self.account_name} ({self.user_id})'


# ---------------------------------------------------------------------------
# Withdrawal
# ---------------------------------------------------------------------------
class Withdrawal(models.Model):
    user_id = models.TextField()  # references users.firebase_uid
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.TextField(default='pending')
    method_type = models.TextField()
    account_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'withdrawals'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f'Withdrawal ₱{self.amount} — {self.status} ({self.user_id})'


# ---------------------------------------------------------------------------
# DeadlineNotification
# ---------------------------------------------------------------------------
class DeadlineNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deadline_notifications', db_column='order_id')
    notification_type = models.TextField()
    sent_to = models.TextField()  # references users.firebase_uid
    sent_at = models.DateTimeField(auto_now_add=True, null=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deadline_notifications'
        managed = False
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.notification_type} for Order #{self.order_id}'


# ---------------------------------------------------------------------------
# DailyAnalytics  (creator analytics per day)
# ---------------------------------------------------------------------------
class DailyAnalytics(models.Model):
    creator_id = models.TextField()  # references users.firebase_uid
    date = models.DateField()
    profile_views = models.IntegerField(default=0, null=True)
    service_clicks = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'daily_analytics'
        managed = False
        unique_together = ('creator_id', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'Analytics for {self.creator_id} on {self.date}'
