from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('<int:pk>/assign/', views.assign_order, name='assign_order'),
]
