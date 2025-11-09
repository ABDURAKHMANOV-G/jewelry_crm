
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CollectionOrderForm
from accounts.models import Customer  # ← Исправленный импорт

# ========================================
# ФУНКЦИЯ РАСЧЕТА ЦЕНЫ ЗАКАЗА
# ========================================
def calculate_order_price(order):
    """
    Рассчитывает estimated_price для заказа
    на основе материала, типа и параметров
    """
    PRICING_CONFIG = {
        'materials': {
            'gold_585': 3500,
            'gold_750': 4200,
            'silver_925': 45,
            'platinum': 8500
        },
        'product_complexity': {
            'ring': 1.0,
            'brooch': 1.3,
            'bracelet': 1.1,
            'earrings': 0.9
        },
        'labor_cost': 0.35
    }

    # Проверка наличия необходимых данных
    if not order.material or not order.product_type:
        return None

    material_price = PRICING_CONFIG['materials'].get(order.material)
    if not material_price:
        return None

    complexity = PRICING_CONFIG['product_complexity'].get(order.product_type, 1.0)

    try:
        if order.order_type == 'template':
            # Расчет для шаблонного заказа
            if order.product_type == 'ring':
                # Примерный вес по размеру кольца
                ring_size = float(order.ring_size or 17)
                weight = max(2, ring_size * 0.4)
            elif order.product_type == 'brooch':
                weight = 8
            elif order.product_type == 'bracelet':
                weight = 12
            elif order.product_type == 'earrings':
                weight = 2
            else:
                weight = 3

            # Коэффициент шаблона (упрощенно)
            coefficient = 1.5
            base_cost = weight * material_price * coefficient

        elif order.order_type == 'custom':
            # Расчет для индивидуального заказа
            weight = float(order.desired_weight or 5)
            if weight <= 0:
                return None
            base_cost = weight * material_price
        else:
            return None

        # Применяем коэффициент сложности и трудозатраты (35%)
        final_price = base_cost * complexity * (1 + PRICING_CONFIG['labor_cost'])
        return round(final_price, 2)

    except (ValueError, TypeError):
        return None


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

                    # 🔴 РАССЧИТЫВАЕМ И СОХРАНЯЕМ ЦЕНУ
                    estimated_price = calculate_order_price(order)
                    if estimated_price:
                        order.estimated_price = estimated_price

                    order.save()

                    messages.success(request, f'Заказ #{order.order_id} успешно создан!')
                    return redirect('order_detail', pk=order.order_id)
            except Exception as e:
                messages.error(request, f'Ошибка при создании заказа: {str(e)}')
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {'form': form})


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
                order = update_form.save(commit=False)
                
                # ✅ ЯВНО СОХРАНЯЕМ ВСЕ ПАРАМЕТРЫ ИЗ ФОРМЫ
                order.ring_size = update_form.cleaned_data.get('ring_size')
                order.thickness = update_form.cleaned_data.get('thickness')
                order.width = update_form.cleaned_data.get('width')
                order.stone_size = update_form.cleaned_data.get('stone_size')
                order.desired_weight = update_form.cleaned_data.get('desired_weight')
                
                # 🔴 ПЕРЕСЧИТЫВАЕМ ЦЕНУ ПРИ ОБНОВЛЕНИИ
                estimated_price = calculate_order_price(order)
                if estimated_price:
                    order.estimated_price = estimated_price
                # 🔴 НОВОЕ: ПРОВЕРЯЕМ БЫЛА ЛИ ЦЕНА УСТАНОВЛЕНА
                if order.final_price and order.final_price > 0:
                    order.price_confirmed = True
                    messages.success(
                        request,
                        f'✅ Цена установлена: {order.final_price:.0f} ₽'
                    )
                order.save()
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

@login_required
def collection_order_create(request, product_id):
    """Создание заказа из коллекции - ТОЛЬКО ДЛЯ КЛИЕНТОВ"""
    
    # Проверка роли пользователя
    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут оформлять заказы из коллекции.')
        return redirect('collection')
    
    # Данные товаров из коллекции
    products = {
        1: {
            'id': 1, 
            'name': 'Étoile', 
            'category': 'ring',  # ← Английское название для БД
            'category_display': 'Кольцо',
            'price': 385000,
            'materials': 'Платина 950, бриллианты 1.2 ct', 
            'tagline': 'Где вечность встречается с элегантностью'
        },
        2: {
            'id': 2, 
            'name': 'Aurora', 
            'category': 'earring',
            'category_display': 'Серьги',
            'price': 520000,
            'materials': 'Белое золото 750, изумруды, бриллианты', 
            'tagline': 'Танец изумрудного пламени'
        },
        3: {
            'id': 3, 
            'name': 'Céleste', 
            'category': 'necklace',
            'category_display': 'Колье',
            'price': 1250000,
            'materials': 'Белое золото 750, сапфир 15 ct', 
            'tagline': 'Небесная симфония сапфиров'
        },
        4: {
            'id': 4, 
            'name': 'Harmonie', 
            'category': 'bracelet',
            'category_display': 'Браслет',
            'price': 245000,
            'materials': 'Розовое золото 585, бриллианты', 
            'tagline': 'Ритм изящества'
        },
        5: {
            'id': 5, 
            'name': 'Lumière', 
            'category': 'pendant',
            'category_display': 'Подвеска',
            'price': 195000,
            'materials': 'Белое золото 750, бриллиант 0.8 ct', 
            'tagline': 'Капля света'
        },
        6: {
            'id': 6, 
            'name': 'Impérial', 
            'category': 'ring',
            'category_display': 'Кольцо',
            'price': 890000,
            'materials': 'Платина 950, рубин 2.5 ct', 
            'tagline': 'Царственное великолепие'
        },
    }
    
    product = products.get(product_id)
    if not product:
        messages.error(request, 'Товар не найден')
        return redirect('collection')
    
    if request.method == 'POST':
        form = CollectionOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # Получаем или создаем Customer для текущего пользователя
            from accounts.models import Customer
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={
                    'first_name': request.user.first_name or 'Клиент',
                    'last_name': request.user.last_name or '',
                    'phone': '',
                    'email': request.user.email or ''
                }
            )
            
            # Заполняем основные поля заказа
            order.customer = customer
            order.order_type = 'collection'  # Тип заказа: "Предзаказ"
            order.product_type = product['category']  # Тип изделия из словаря
            
            # Информация о товаре из коллекции
            order.collection_product_id = product['id']
            order.collection_product_name = product['name']
            order.collection_product_price = product['price']
            order.estimated_price = product['price']
            order.material = product['materials']
            
            # Размер изделия (если указан)
            ring_size = form.cleaned_data.get('ring_size')
            if ring_size and ring_size != 'custom':
                order.ring_size = ring_size
            
            # Комментарий
            comment = form.cleaned_data.get('comment')
            if comment:
                order.comment = comment
            
            # Статус заказа
            order.status = 'pending'
            
            try:
                order.save()
                messages.success(
                    request, 
                    f'✨ Заказ на "{product["name"]}" успешно оформлен! '
                    f'Наш менеджер свяжется с вами в ближайшее время.'
                )
                return redirect('order_detail', pk=order.order_id)
            except Exception as e:
                messages.error(request, f'Ошибка при создании заказа: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CollectionOrderForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'orders/collection_order_create.html', context)

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
        # Предзаполнение суммой из бюджета или final_price заказа
        initial_data = {}
        if order.final_price:
            initial_data['amount'] = order.final_price
        elif order.budget:
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

@manager_required
def generate_modeler_brief(request, pk):
    """
    Генерация ТЗ для модельера - ТОЛЬКО ДЛЯ МЕНЕДЖЕРА
    """
    order = get_object_or_404(Order, pk=pk)
    
    # Импортируем функцию генерации
    from .document_generator import generate_brief_pdf
    
    # Генерируем PDF
    pdf_buffer = generate_brief_pdf(order)
    
    # Формируем имя файла
    filename = f"ТЗ_Заказ_{order.order_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Возвращаем PDF для скачивания
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)