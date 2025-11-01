"""
Декораторы и миксины для проверки ролей пользователей
"""
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from functools import wraps


# ========================================
# ЧАСТЬ 1: ДЕКОРАТОРЫ (для функций-views)
# ========================================

def role_required(*roles):
    """
    Декоратор для проверки роли пользователя
    Использование: @role_required('client', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Необходимо войти в систему.')
                return redirect('login')
            
            if request.user.role not in roles:
                messages.error(request, 'У вас нет прав для доступа к этой странице.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def client_required(view_func):
    """Доступ только для клиентов"""
    return role_required('client')(view_func)


def manager_required(view_func):
    """Доступ только для менеджеров"""
    return role_required('manager')(view_func)


def worker_required(view_func):
    """Доступ для модельеров и ювелиров"""
    return role_required('modeler', 'jeweler')(view_func)


def staff_required(view_func):
    """Доступ для всех сотрудников (кроме клиентов)"""
    return role_required('manager', 'modeler', 'jeweler')(view_func)


# ========================================
# ЧАСТЬ 2: МИКСИНЫ (для классов-views)
# ========================================
# Эти классы нужны ТОЛЬКО если будете использовать Class-Based Views
# Пока что не используются, но на будущее

class RoleRequiredMixin(UserPassesTestMixin):
    """Базовый миксин для проверки роли"""
    allowed_roles = []
    
    def test_func(self):
        return self.request.user.role in self.allowed_roles
    
    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для доступа к этой странице.')
        return redirect('home')


class ClientRequiredMixin(RoleRequiredMixin):
    """Доступ только для клиентов"""
    allowed_roles = ['client']


class ManagerRequiredMixin(RoleRequiredMixin):
    """Доступ только для менеджеров"""
    allowed_roles = ['manager']


class WorkerRequiredMixin(RoleRequiredMixin):
    """Доступ для модельеров и ювелиров"""
    allowed_roles = ['modeler', 'jeweler']


class StaffRequiredMixin(RoleRequiredMixin):
    """Доступ для всех сотрудников"""
    allowed_roles = ['manager', 'modeler', 'jewelier']
