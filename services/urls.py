from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('create/', views.service_create, name='service_create'),
    path('my/', views.my_services, name='my_services'),
]
