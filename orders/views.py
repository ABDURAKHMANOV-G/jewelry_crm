from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, Product, OrderProduct
from .forms import OrderCreateForm, OrderUpdateForm
from accounts.models import Customer, User
from accounts.decorators import client_required, manager_required

@login_required
def order_list(request):
    """Список заказов (доступно всем авторизованным)"""
    if request.user.role == 'client':
        customer = Customer.objects.filter(user=request.user).first()
        if customer:
            orders = Order.objects.filter(customer=customer).order_by('-order_id')
        else:
            orders = []
    elif request.user.role == 'manager':
        orders = Order.objects.all().order_by('-order_id')
    else:  # modeler, jeweler
        orders = Order.objects.filter(user=request.user).order_by('-order_id')
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@client_required
def order_create(request):
    """Создание заказа - ТОЛЬКО ДЛЯ КЛИЕНТОВ"""
    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        messages.error(request, 'Профиль клиента не найден. Обратитесь к администратору.')
        return redirect('home')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.customer = customer
                    order.order_status = 'new'
                    order.save()
                    
                    messages.success(request, f'Заказ #{order.order_id} успешно создан!')
                    return redirect('order_detail', pk=order.order_id)
            except Exception as e:
                messages.error(request, f'Ошибка при создании заказа: {str(e)}')
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order_create_new.html', {'form': form})


@login_required
def order_detail(request, pk):
    """Детали заказа - с проверкой прав доступа"""
    order = get_object_or_404(Order, pk=pk)
    
    # ПРОВЕРКА ПРАВ ДОСТУПА
    if request.user.role == 'client':
        # Клиент видит только свои заказы
        if not order.customer or order.customer.user != request.user:
            messages.error(request, 'У вас нет доступа к этому заказу.')
            return redirect('order_list')
    
    elif request.user.role in ['modeler', 'jeweler']:
        # Модельер/Ювелир видит только назначенные ему заказы
        if order.user != request.user:
            messages.error(request, 'Этот заказ не назначен вам.')
            return redirect('order_list')
    
    # Менеджер видит все заказы
    
    # Форма редактирования ТОЛЬКО ДЛЯ МЕНЕДЖЕРА
    update_form = None
    if request.user.role == 'manager':
        if request.method == 'POST':
            update_form = OrderUpdateForm(request.POST, instance=order)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, 'Заказ обновлен!')
                return redirect('order_detail', pk=pk)
        else:
            update_form = OrderUpdateForm(instance=order)
    
    order_products = order.order_products.all()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_products': order_products,
        'update_form': update_form
    })


@login_required
def order_delete(request, pk):
    """Удаление заказа - клиент или менеджер"""
    order = get_object_or_404(Order, pk=pk)
    
    # ПРОВЕРКА ПРАВ
    if request.user.role == 'client':
        # Клиент может удалять ТОЛЬКО свои новые заказы
        if not order.customer or order.customer.user != request.user:
            messages.error(request, 'У вас нет прав на удаление этого заказа.')
            return redirect('order_list')
        
        if order.order_status != 'new':
            messages.error(request, 'Можно удалять только новые заказы.')
            return redirect('order_detail', pk=pk)
    
    elif request.user.role == 'manager':
        # Менеджер может удалять любые заказы
        pass
    
    else:
        # Модельер/Ювелир не может удалять заказы
        messages.error(request, 'У вас нет прав на удаление заказов.')
        return redirect('order_list')
    
    if request.method == 'POST':
        order_id = order.order_id
        order.delete()
        messages.success(request, f'Заказ #{order_id} удален.')
        return redirect('order_list')
    
    return render(request, 'orders/order_confirm_delete.html', {'order': order})


@manager_required
def assign_order(request, pk):
    """Назначение заказа исполнителю - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        if worker_id:
            worker = get_object_or_404(User, user_id=worker_id, role__in=['modeler', 'jeweler'])
            order.user = worker
            order.order_status = 'in_work'
            order.save()
            messages.success(request, f'Заказ назначен исполнителю {worker.username}')
        return redirect('order_detail', pk=pk)
    
    workers = User.objects.filter(role__in=['modeler', 'jeweler'], is_active=True)
    return render(request, 'orders/assign_order.html', {
        'order': order,
        'workers': workers
    })
