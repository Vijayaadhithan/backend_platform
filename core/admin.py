from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, ServiceProvider, ServiceType, Booking, Product, ProductCategory,
    Order, OrderItem, Payment, Membership, UserMembership, Review,
    Notification, LoyaltyProgram
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'membership_status', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('membership_status', 'is_staff', 'is_active')

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'location', 'rating')
    search_fields = ('name', 'location')
    list_filter = ('service_type',)

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'unit_price')
    search_fields = ('name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_provider', 'service_type', 'scheduled_time', 'status', 'price')
    search_fields = ('user__username', 'service_provider__name')
    list_filter = ('status', 'created_at')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'category')
    search_fields = ('name', 'description')
    list_filter = ('category',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    list_filter = ('status', 'payment_method')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    search_fields = ('name',)

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership', 'start_date', 'end_date', 'status')
    search_fields = ('user__username',)
    list_filter = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_provider', 'rating', 'created_at')
    search_fields = ('user__username', 'service_provider__name')
    list_filter = ('rating',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'status', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('notification_type', 'status')

@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'tier', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('tier',)
