from django.contrib import admin
from .models import Order, Review

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user', 'service', 'appointment_date', 'status', 'total_price')
    list_filter = ('status',)
    search_fields = ('order_no',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
