from django.db import models
from accounts.models import User, Customer

class Product(models.Model):
    product_id = models.AutoField(primary_key=True, db_column='product_id')
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.product_name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, db_column='order_id')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='user_id')
    
    ORDER_STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('in_work', 'В работе'),
        ('ready', 'Готов'),
        ('delivered', 'Доставлен'),
    ]
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='new')
    
    # НОВЫЕ ПОЛЯ
    PRODUCT_TYPE_CHOICES = [
        ('ring', 'Кольцо'),
        ('brooch', 'Брошь'),
        ('bracelet', 'Браслет'),
        ('earrings', 'Серьги'),
    ]
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, null=True, blank=True, verbose_name='Тип изделия')
    
    ORDER_TYPE_CHOICES = [
        ('template', 'Шаблонный'),
        ('custom', 'Индивидуальный'),
    ]
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, null=True, blank=True, verbose_name='Тип заказа')
    
    # Поля для шаблонного заказа
    template_image = models.CharField(max_length=200, null=True, blank=True, verbose_name='Изображение шаблона')
    
    # Поля для индивидуального заказа
    ring_size = models.CharField(max_length=10, null=True, blank=True, verbose_name='Размер')
    thickness = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Толщина (мм)')
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ширина (мм)')
    stone_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Размер камня (карат)')
    desired_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Желаемый вес (г)')
    
    # Общие поля
    material = models.CharField(max_length=50, null=True, blank=True, verbose_name='Материал')
    
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    required_by = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий/Уточнения')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ #{self.order_id}"

    def get_status_display_ru(self):
        status_map = {
            'new': 'Новый',
            'confirmed': 'Подтвержден',
            'in_work': 'В работе',
            'ready': 'Готов',
            'delivered': 'Доставлен',
        }
        return status_map.get(self.order_status, self.order_status)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products', db_column='order_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')

    class Meta:
        managed = False
        db_table = 'orders_products'  # ← С ПОДЧЁРКИВАНИЕМ!
        unique_together = (('order', 'product'),)



class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True, db_column='payment_id')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'payments'
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'


class Document(models.Model):
    document_id = models.AutoField(primary_key=True, db_column='document_id')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    document_type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'documents'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
