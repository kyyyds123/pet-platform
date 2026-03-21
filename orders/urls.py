from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('create/<int:service_id>/', views.order_create, name='order_create'),
    path('<int:pk>/status/', views.order_status, name='order_status'),
    path('<int:order_id>/review/', views.review_create, name='review_create'),
    path('<int:order_id>/add-record/', views.order_add_record, name='order_add_record'),

    # 管理员评价管理
    path('admin/reviews/', views.admin_review_list, name='admin_reviews'),
    path('admin/reviews/<int:pk>/approve/', views.admin_review_approve, name='admin_review_approve'),
    path('admin/reviews/<int:pk>/reject/', views.admin_review_reject, name='admin_review_reject'),
]
