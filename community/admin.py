from django.contrib import admin
from .models import Post, Comment, LostPet

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'likes_count', 'is_pinned', 'created_at')
    list_filter = ('post_type', 'is_pinned')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')

@admin.register(LostPet)
class LostPetAdmin(admin.ModelAdmin):
    list_display = ('pet_name', 'author', 'status', 'location', 'created_at')
    list_filter = ('status',)
