from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/like/', views.post_like, name='post_like'),
    path('posts/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('lost/', views.lost_pet_list, name='lost_list'),
    path('lost/create/', views.lost_pet_create, name='lost_create'),
    path('lost/<int:pk>/update/', views.lost_pet_update, name='lost_update'),
]
