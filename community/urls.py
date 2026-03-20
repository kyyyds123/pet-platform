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

    # 管理员审核
    path('admin/posts/', views.admin_post_list, name='admin_posts'),
    path('admin/posts/<int:pk>/pin/', views.admin_post_pin, name='admin_post_pin'),
    path('admin/posts/<int:pk>/delete/', views.admin_post_delete, name='admin_post_delete'),
    path('admin/comments/', views.admin_comment_list, name='admin_comments'),
    path('admin/comments/<int:pk>/delete/', views.admin_comment_delete, name='admin_comment_delete'),
    path('admin/lost/', views.admin_lost_list, name='admin_lost'),
    path('admin/lost/<int:pk>/delete/', views.admin_lost_delete, name='admin_lost_delete'),
]
