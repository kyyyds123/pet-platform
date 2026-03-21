from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/like/', views.article_like, name='article_like'),
    path('<int:pk>/favorite/', views.article_favorite, name='article_favorite'),
]
