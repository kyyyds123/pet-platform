from django.contrib import admin
from .models import Pet, VaccineRecord

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'breed', 'gender', 'created_at')
    search_fields = ('name', 'breed')

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'record_type', 'name', 'date', 'next_date', 'is_reminded')
    list_filter = ('record_type', 'is_reminded')
