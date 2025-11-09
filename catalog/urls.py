from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.collection_view, name='collection'),
    path('collection/product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('collection/masterpiece/', views.masterpiece_view, name='masterpiece'),  # ← Новый URL
]