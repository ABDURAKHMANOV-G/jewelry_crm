from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, Product, OrderProduct
from .forms import OrderCreateForm, OrderUpdateForm
from accounts.models import Customer, User
from accounts.decorators import client_required, manager_required
from .models import Document
from .forms import DocumentCreateForm, DocumentUpdateForm
from datetime import datetime
from .document_generator import generate_invoice_pdf, generate_act_pdf, generate_contract_pdf
from django.http import FileResponse
from .reports import generate_report_data, generate_report_pdf
from datetime import datetime, timedelta

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


@login_required
def document_list(request, order_id):
    """Список документов заказа"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Проверка прав доступа
    if request.user.role == 'client':
        if not order.customer or order.customer.user != request.user:
            messages.error(request, 'У вас нет доступа к этому заказу.')
            return redirect('order_list')
    
    documents = Document.objects.filter(order=order).order_by('-document_date')
    
    return render(request, 'orders/document_list.html', {
        'order': order,
        'documents': documents
    })


@manager_required
def document_create(request, order_id):
    """Создание документа - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        form = DocumentCreateForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.order = order
            document.created_by = request.user
            
            # Авто-генерация номера документа если не указан
            if not document.document_number:
                doc_type_prefix = {
                    'invoice': 'СЧ',
                    'receipt': 'ЧЕК',
                    'act': 'АКТ',
                    'contract': 'ДОГ',
                }.get(document.document_type, 'ДОК')
                
                document.document_number = f"{doc_type_prefix}-{order.order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            document.save()
            messages.success(request, f'Документ {document.document_number} успешно создан!')
            return redirect('document_list', order_id=order.order_id)
    else:
        # Предзаполнение суммой из бюджета заказа
        initial_data = {}
        if order.budget:
            initial_data['amount'] = order.budget
        form = DocumentCreateForm(initial=initial_data)
    
    return render(request, 'orders/document_create.html', {
        'form': form,
        'order': order
    })
    
def document_export_pdf(request, pk):
    """Экспорт документа в PDF"""
    document = get_object_or_404(Document, pk=pk)
    order = document.order
    
    # Выбираем генератор по типу документа
    if document.document_type == 'invoice':
        pdf_buffer = generate_invoice_pdf(order, document)
        filename = f"Счёт_{document.document_number}.pdf"
    elif document.document_type == 'act':
        pdf_buffer = generate_act_pdf(order, document)
        filename = f"Акт_{document.document_number}.pdf"
    elif document.document_type == 'contract':
        pdf_buffer = generate_contract_pdf(order, document)
        filename = f"Договор_{document.document_number}.pdf"
    else:
        filename = f"Документ_{document.document_number}.pdf"
        pdf_buffer = generate_invoice_pdf(order, document)
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


@manager_required
def document_update(request, pk):
    """Редактирование документа - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentUpdateForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Документ обновлён!')
            return redirect('document_list', order_id=document.order.order_id)
    else:
        form = DocumentUpdateForm(instance=document)
    
    return render(request, 'orders/document_update.html', {
        'form': form,
        'document': document
    })


@manager_required
def document_delete(request, pk):
    """Удаление документа - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    document = get_object_or_404(Document, pk=pk)
    order_id = document.order.order_id
    
    if request.method == 'POST':
        document_number = document.document_number
        document.delete()
        messages.success(request, f'Документ {document_number} удалён.')
        return redirect('document_list', order_id=order_id)
    
    return render(request, 'orders/document_confirm_delete.html', {
        'document': document
    })
    
    
@manager_required
def report_form(request):
    """Форма для выбора периода отчёта - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    return render(request, 'orders/report_form.html')


@manager_required
def report_generate(request):
    """Генерация и просмотр отчёта - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    # Получаем даты из запроса
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Валидация дат
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except:
        messages.error(request, 'Неверный формат дат.')
        return redirect('report_form')
    
    # Вычисляем количество дней
    period_days = (end_date - start_date).days + 1
    
    # Получаем заказы за период
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Генерируем данные отчёта
    report_data = generate_report_data(orders)
    
    return render(request, 'orders/report_view.html', {
        'start_date': start_date,
        'end_date': end_date,
        'period_days': period_days,
        'report_data': report_data,
        'orders': orders,
        'now': datetime.now(),
    })


@manager_required
def report_export_pdf(request):
    """Экспорт отчёта в PDF - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except:
        messages.error(request, 'Неверный формат дат.')
        return redirect('report_form')
    
    # Получаем заказы
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    # Генерируем данные
    report_data = generate_report_data(orders)
    
    # Генерируем PDF
    pdf_buffer = generate_report_pdf(start_date, end_date, report_data)
    
    filename = f"Отчёт_{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)