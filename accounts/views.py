from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .forms import UserRegistrationForm
from .models import Customer, User
from .decorators import client_required, manager_required
from orders.models import Order

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя
            user = form.save(commit=False)
            user.role = 'client'
            user.save()
            
            # Получаем телефон из формы
            phone = form.cleaned_data.get('phone', '')
            print(f"DEBUG: Сохраняем телефон: '{phone}'")
            
            # Получаем или создаем профиль клиента
            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.first_name,
                    'surname': user.last_name,
                    'email': user.email,
                    'phone': phone if phone else None
                }
            )
            
            # Если профиль уже существовал - обновляем его
            if not created:
                customer.name = user.first_name
                customer.surname = user.last_name
                customer.email = user.email
                customer.phone = phone if phone else None
                customer.save()
                print(f"DEBUG: Customer обновлен с ID: {customer.customer_id}, телефон: {customer.phone}")
            else:
                print(f"DEBUG: Customer создан с ID: {customer.customer_id}, телефон: {customer.phone}")
            
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('home')
        else:
            print(f"DEBUG: Ошибки формы: {form.errors}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def register_view(request):
    """Алиас для register"""
    return register(request)


def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


@login_required
def home_view(request):
    """Главная страница"""
    return render(request, 'home.html')



@manager_required
def customer_list(request):
    """Список всех клиентов - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    customers = Customer.objects.select_related('user').all()
    
    # Фильтрация
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(surname__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Добавляем количество заказов для каждого клиента
    customers = customers.annotate(orders_count=Count('order'))
    
    return render(request, 'accounts/customer_list.html', {
        'customers': customers,
        'search': search
    })


@manager_required
def customer_orders(request, customer_id):
    """Список заказов конкретного клиента - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    customer = get_object_or_404(Customer, customer_id=customer_id)
    orders = Order.objects.filter(customer=customer).order_by('-order_id')
    
    # Фильтрация заказов
    status_filter = request.GET.get('status', '')
    order_type_filter = request.GET.get('order_type', '')
    product_type_filter = request.GET.get('product_type', '')
    
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    if order_type_filter:
        orders = orders.filter(order_type=order_type_filter)
    
    if product_type_filter:
        orders = orders.filter(product_type=product_type_filter)
    
    return render(request, 'accounts/customer_orders.html', {
        'customer': customer,
        'orders': orders,
        'status_filter': status_filter,
        'order_type_filter': order_type_filter,
        'product_type_filter': product_type_filter
    })
