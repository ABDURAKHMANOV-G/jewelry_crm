from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.collection_view, name='collection'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
]
