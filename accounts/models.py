from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Пользователь системы (клиенты, менеджеры, модельеры, ювелиры)"""
    
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('manager', 'Менеджер'),
        ('modeler', 'Модельер'),
        ('jeweler', 'Ювелир'),
    )
    
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    role = models.CharField(
        max_length=150,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_client(self):
        """Проверка: является ли пользователь клиентом"""
        return self.role == 'client'
    
    def is_manager(self):
        """Проверка: является ли пользователь менеджером"""
        return self.role == 'manager'
    
    def is_worker(self):
        """Проверка: является ли пользователь модельером или ювелиром"""
        return self.role in ['modeler', 'jeweler']


class Customer(models.Model):
    """Расширенный профиль клиента (создается автоматически для role='client')"""
    
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        db_column='user_id',
        related_name='customer_profile',
        verbose_name='Пользователь'
    )
    surname = models.CharField(max_length=150, blank=True, null=True, verbose_name='Фамилия')
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Имя')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    email = models.CharField(max_length=100, blank=True, null=True, verbose_name='Email')
    order_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Название заказа')
    role = models.CharField(max_length=150, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'customers'
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'
    
    def __str__(self):
        return f"{self.surname} {self.name}" if self.surname else f"Клиент #{self.customer_id}"
    
    def get_full_name(self):
        """Получить полное имя клиента"""
        return f"{self.surname} {self.name}".strip()


# Автоматическое создание профиля клиента при регистрации
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Создать профиль клиента автоматически при регистрации пользователя с role='client'"""
    if created and instance.role == 'client':
        # Создаем запись в таблице customers
        Customer.objects.create(
            user=instance,
            email=instance.email,
            name=instance.first_name,
            surname=instance.last_name
        )
