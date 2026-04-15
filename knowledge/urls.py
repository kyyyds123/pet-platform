from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/like/', views.article_like, name='article_like'),
    path('<int:pk>/favorite/', views.article_favorite, name='article_favorite'),
    # 管理员
    path('admin/articles/', views.admin_article_list, name='admin_articles'),
    path('admin/articles/create/', views.admin_article_create, name='admin_article_create'),
    path('admin/articles/<int:pk>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('admin/articles/<int:pk>/delete/', views.admin_article_delete, name='admin_article_delete'),
]
