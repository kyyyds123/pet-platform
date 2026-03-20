from django.contrib import admin
from .models import ServiceCategory, Service

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'sort_order')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'price', 'is_active', 'avg_rating')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
