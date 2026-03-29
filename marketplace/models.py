from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ---------------------------------------------------------------------------
# Custom User Manager
# ---------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


# ---------------------------------------------------------------------------
# User Model  (roles: client | creator | admin)
# ---------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('creator', 'Creator'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    is_verified = models.BooleanField(default=False)
    reports = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=[('Active', 'Active'), ('Warning', 'Warning'), ('Suspended', 'Suspended')],
        default='Active',
    )
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


# ---------------------------------------------------------------------------
# Service  (offered by a Creator)
# ---------------------------------------------------------------------------
class Service(models.Model):
    CATEGORY_CHOICES = [
        ('design', 'Design'),
        ('development', 'Development'),
        ('photography', 'Photography'),
        ('video', 'Video & Animation'),
        ('writing', 'Writing & Content'),
        ('marketing', 'Marketing'),
        ('music', 'Music & Audio'),
        ('other', 'Other'),
    ]

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='services',
        limit_choices_to={'role': 'creator'},
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    delivery_days = models.PositiveIntegerField(default=7)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} by {self.creator.full_name}'


# ---------------------------------------------------------------------------
# Order  (client places an order for a creator's service)
# ---------------------------------------------------------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    ]

    client = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='orders_placed',
        limit_choices_to={'role': 'client'},
    )
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='orders_received',
        limit_choices_to={'role': 'creator'},
    )
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    # Snapshot fields — preserved even if service is deleted
    service_title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        client_name = self.client.full_name if self.client else 'Unknown'
        return f'Order #{self.pk} — {self.service_title} ({client_name})'

    @property
    def client_name(self):
        return self.client.full_name if self.client else ''

    @property
    def creator_name(self):
        return self.creator.full_name if self.creator else ''


# ---------------------------------------------------------------------------
# Project  (creator-managed, visible to clients + admin)
# ---------------------------------------------------------------------------
class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Suspended', 'Suspended'),
    ]

    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='projects',
    )
    title = models.CharField(max_length=200)
    client_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} (Client: {self.client_name})'

    @property
    def platform_fee(self):
        return float(self.budget) * 0.15


# ---------------------------------------------------------------------------
# WalletTransaction  (deposit / withdrawal / payment / earning)
# ---------------------------------------------------------------------------
class WalletTransaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('earning', 'Earning'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_type} ₱{self.amount} — {self.user.email}'
