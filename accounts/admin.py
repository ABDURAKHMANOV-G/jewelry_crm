from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для пользователей"""
    
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'created_at')}),
    )
    
    readonly_fields = ('created_at', 'last_login', 'date_joined')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Админка для профилей клиентов"""
    
    list_display = ('customer_id', 'get_username', 'surname', 'name', 'phone', 'email')
    search_fields = ('surname', 'name', 'phone', 'email', 'user__username')
    list_filter = ('role',)
    
    def get_username(self, obj):
        return obj.user.username if obj.user else '-'
    get_username.short_description = 'Username'
