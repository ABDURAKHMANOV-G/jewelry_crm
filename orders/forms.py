from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    # Выбор типа изделия
    product_type = forms.ChoiceField(
        choices=[('', 'Выберите тип изделия')] + list(Order.PRODUCT_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_product_type'}),
        label='Тип изделия'
    )
    
    # Выбор типа заказа
    order_type = forms.ChoiceField(
        choices=[('', 'Выберите тип заказа')] + list(Order.ORDER_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_order_type'}),
        label='Тип заказа'
    )
    
    # Поля для шаблонного заказа
    template_image = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_template_image'}),
        label='Выберите шаблон'
    )
    
    # Материал (общее)
    MATERIAL_CHOICES = [
        ('', 'Выберите материал'),
        ('gold_585', 'Золото 585'),
        ('gold_750', 'Золото 750'),
        ('silver_925', 'Серебро 925'),
        ('platinum', 'Платина'),
    ]
    material = forms.ChoiceField(
        choices=MATERIAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Материал'
    )
    
    # Поля для индивидуального заказа
    ring_size = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 17'}),
        label='Размер'
    )
    
    thickness = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'мм', 'step': '0.1'}),
        label='Толщина'
    )
    
    width = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'мм', 'step': '0.1'}),
        label='Ширина'
    )
    
    stone_size = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'карат', 'step': '0.01'}),
        label='Размер камня'
    )
    
    desired_weight = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'грамм', 'step': '0.1'}),
        label='Желаемый вес'
    )
    
    # Комментарий
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Опишите дополнительные пожелания или уточнения'
        }),
        label='Комментарий'
    )
    
    # Бюджет и срок
    budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ваш бюджет'}),
        label='Бюджет (₽)'
    )
    
    required_by = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Желаемая дата готовности'
    )

    class Meta:
        model = Order
        fields = [
            'product_type', 'order_type', 'template_image',
            'ring_size', 'thickness', 'width', 'stone_size', 'desired_weight',
            'material', 'comment', 'budget', 'required_by'
        ]


class OrderUpdateForm(forms.ModelForm):
    ORDER_STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('in_work', 'В работе'),
        ('ready', 'Готов'),
        ('delivered', 'Доставлен'),
    ]
    
    order_status = forms.ChoiceField(
        choices=ORDER_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Статус заказа'
    )
    
    user = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Исполнитель'
    )
    
    # Тип изделия и тип заказа
    product_type = forms.ChoiceField(
        choices=[('', '------')] + list(Order.PRODUCT_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тип изделия'
    )
    
    order_type = forms.ChoiceField(
        choices=[('', '------')] + list(Order.ORDER_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Тип заказа'
    )
    
    # Шаблонный заказ
    template_image = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Шаблон изображения'
    )
    
    # Материал
    MATERIAL_CHOICES = [
        ('', '------'),
        ('gold_585', 'Золото 585'),
        ('gold_750', 'Золото 750'),
        ('silver_925', 'Серебро 925'),
        ('platinum', 'Платина'),
    ]
    material = forms.ChoiceField(
        choices=MATERIAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Материал'
    )
    
    # Индивидуальный заказ
    ring_size = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 17'}),
        label='Размер'
    )
    
    thickness = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'мм', 'step': '0.1'}),
        label='Толщина (мм)'
    )
    
    width = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'мм', 'step': '0.1'}),
        label='Ширина (мм)'
    )
    
    stone_size = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'карат', 'step': '0.01'}),
        label='Размер камня (карат)'
    )
    
    desired_weight = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'грамм', 'step': '0.1'}),
        label='Желаемый вес (г)'
    )
    
    # Комментарий
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        }),
        label='Комментарий'
    )
    
    # Бюджет и срок
    budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Бюджет (₽)'
    )
    
    required_by = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Срок выполнения'
    )
    
    class Meta:
        model = Order
        fields = [
            'order_status', 'user', 
            'product_type', 'order_type', 'template_image',
            'ring_size', 'thickness', 'width', 'stone_size', 'desired_weight',
            'material', 'comment', 'budget', 'required_by'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['user'].queryset = User.objects.filter(role__in=['modeler', 'jeweler'])
