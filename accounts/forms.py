from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    
    # ВАЖНО: Поле phone НЕ из модели User, а отдельное
    phone = forms.CharField(
        max_length=20,
        required=False,  # Необязательное
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+7 (___) ___-__-__'
        })
    )

    class Meta:
        model = User
        # ВАЖНО: НЕ включаем phone в fields, т.к. его нет в модели User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтвердите пароль'})
    
    # ДОБАВИМ метод для отладки
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        print(f"DEBUG: Телефон из формы: '{phone}'")  # Для отладки
        return phone
