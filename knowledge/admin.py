from django.contrib import admin
from .models import KnowledgeCategory, KnowledgeArticle

@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'sort_order')

@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'view_count', 'is_hot', 'created_at')
    list_filter = ('category', 'is_hot')
    search_fields = ('title',)
