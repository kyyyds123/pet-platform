from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_page, name='chat'),
    path('reply/', views.chatbot_reply, name='reply'),
    path('manual/', views.request_manual, name='request_manual'),

    # 管理员
    path('admin/chats/', views.admin_chat_list, name='admin_chats'),
    path('admin/chats/<str:session_key>/', views.admin_chat_detail, name='admin_chat_detail'),
    path('admin/manual/', views.admin_manual_list, name='admin_manual'),
    path('admin/manual/<int:pk>/respond/', views.admin_manual_respond, name='admin_manual_respond'),
    path('admin/manual/<int:pk>/close/', views.admin_manual_close, name='admin_manual_close'),
    path('admin/manual/<int:pk>/send/', views.admin_send_message, name='admin_send_message'),
]
