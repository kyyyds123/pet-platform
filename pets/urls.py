from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('', views.pet_list, name='pet_list'),
    path('create/', views.pet_create, name='pet_create'),
    path('<int:pk>/', views.pet_detail, name='pet_detail'),
    path('<int:pk>/edit/', views.pet_edit, name='pet_edit'),
    path('<int:pet_id>/record/', views.record_create, name='record_create'),
    path('reminders/', views.reminders, name='reminders'),
    path('reminders/<int:pk>/done/', views.mark_reminded, name='mark_reminded'),
]
