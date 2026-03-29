from django.contrib import admin

from .models import Order, Project, Service, User, WalletTransaction


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'status', 'is_verified', 'wallet_balance', 'date_joined']
    list_filter = ['role', 'status', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Account', {'fields': ('email', 'password', 'role', 'status', 'is_verified', 'is_staff', 'is_active')}),
        ('Personal Info', {'fields': ('first_name', 'middle_name', 'last_name', 'phone', 'birth_date')}),
        ('Financial', {'fields': ('wallet_balance', 'reports')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'price', 'delivery_days', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'creator__email', 'creator__first_name', 'creator__last_name']
    ordering = ['-created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_title', 'client', 'creator', 'price', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['service_title', 'client__email', 'creator__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client_name', 'creator', 'status', 'budget', 'deadline', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'client_name', 'creator__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    def platform_fee(self, obj):
        return f'₱{obj.platform_fee:,.2f}'
    platform_fee.short_description = 'Platform Fee (15%)'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'description', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__email', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
