from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('<int:pk>/assign/', views.assign_order, name='assign_order'),
    
    # Документы
    path('<int:order_id>/documents/', views.document_list, name='document_list'),
    path('<int:order_id>/documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/update/', views.document_update, name='document_update'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:pk>/export-pdf/', views.document_export_pdf, name='document_export_pdf'),
    
    # Отчёты
    path('reports/', views.report_form, name='report_form'),
    path('reports/generate/', views.report_generate, name='report_generate'),
    path('reports/export-pdf/', views.report_export_pdf, name='report_export_pdf'),
    
    path('order/<int:pk>/generate-brief/', views.generate_modeler_brief, name='generate_modeler_brief'),
    path('collection-order/<int:product_id>/', views.collection_order_create, name='collection_order_create'),
]
