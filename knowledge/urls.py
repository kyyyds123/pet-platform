from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
]
