from django.contrib import admin
from .models import Product, Order, OrderProduct, Payment, Document

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'product_name', 'category', 'base_price']
    list_filter = ['category']
    search_fields = ['product_name', 'category']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'product_type', 'order_type', 'order_status', 'created_at']
    list_filter = ['order_status', 'product_type', 'order_type', 'created_at']
    search_fields = ['order_id', 'customer__name', 'customer__surname']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('customer', 'user', 'order_status')
        }),
        ('Тип изделия', {
            'fields': ('product_type', 'order_type')
        }),
        ('Шаблонный заказ', {
            'fields': ('template_image',),
            'classes': ('collapse',)
        }),
        ('Индивидуальный заказ', {
            'fields': ('ring_size', 'thickness', 'width', 'stone_size', 'desired_weight'),
            'classes': ('collapse',)
        }),
        ('Общие параметры', {
            'fields': ('material', 'comment', 'budget', 'required_by')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['order__order_id']
    date_hierarchy = 'payment_date'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_id', 'order', 'document_type', 'file_path', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['order__order_id', 'document_type']
    date_hierarchy = 'uploaded_at'


# OrderProduct не регистрируем в админке (это связующая таблица)
# Можно использовать inline если нужно
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1
