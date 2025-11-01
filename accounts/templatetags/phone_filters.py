from django import template
import re

register = template.Library()

@register.filter(name='format_phone')
def format_phone(phone):
    """
    Форматирует телефон в формат +7 (XXX) XXX-XX-XX
    Примеры:
        89640124733 -> +7 (964) 012-47-33
        +79640124733 -> +7 (964) 012-47-33
        79640124733 -> +7 (964) 012-47-33
    """
    if not phone:
        return '-'
    
    # Убираем все символы кроме цифр
    digits = re.sub(r'\D', '', str(phone))
    
    # Если начинается с 8, заменяем на 7
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    
    # Если не начинается с 7, добавляем 7 в начало
    if not digits.startswith('7'):
        digits = '7' + digits
    
    # Проверяем длину (должно быть 11 цифр для российского номера)
    if len(digits) != 11:
        return phone  # Возвращаем как есть, если формат неправильный
    
    # Форматируем: +7 (XXX) XXX-XX-XX
    formatted = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    
    return formatted
