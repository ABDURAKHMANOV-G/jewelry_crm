from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os

# Регистрируем шрифты
try:
    windows_fonts_path = r'C:\Windows\Fonts'
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(windows_fonts_path, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(windows_fonts_path, 'arialbd.ttf')))
    FONT_NAME = 'Arial'
    FONT_NAME_BOLD = 'Arial-Bold'
except:
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'

# Реквизиты компании
COMPANY_NAME = "ООО «JEWEllUX»"
COMPANY_ADDRESS = "123456, г. Москва, ул. Золотая, д. 10, офис 1"
COMPANY_PHONE = "+7 (999) 123-45-67"
COMPANY_EMAIL = "info@jewelux.com"
COMPANY_INN = "7701234567"
COMPANY_KPP = "770101001"
COMPANY_OGRN = "1107746000001"
BANK_NAME = "ПАО Сбербанк"
BANK_BIK = "044525225"
BANK_ACCOUNT = "40702810700000000000"
BANK_CORR_ACCOUNT = "30101810400000000225"
DIRECTOR_NAME = "Генеральный директор"
DIRECTOR_FIO = "АБдурахманов Г.Г."


def num_to_words_ru(number):
    """Конвертирует число в пропись на русском"""
    if number == 0:
        return 'ноль'
    
    units = ['', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']
    units_fem = ['', 'одна', 'две', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']
    teens = ['десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 
             'пятнадцать', 'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать']
    tens = ['', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят', 
            'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто']
    hundreds = ['', 'сто', 'двести', 'триста', 'четыреста', 
                'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот']
    
    def convert_below_thousand(num, use_feminine=False):
        """Конвертирует числа до 999"""
        result = []
        
        # Сотни
        h = num // 100
        if h > 0:
            result.append(hundreds[h])
        
        # Десятки и единицы
        remainder = num % 100
        
        if 10 <= remainder <= 19:
            # От 10 до 19
            result.append(teens[remainder - 10])
        else:
            # Десятки
            t = remainder // 10
            if t > 0:
                result.append(tens[t])
            
            # Единицы
            u = remainder % 10
            if u > 0:
                unit_list = units_fem if use_feminine else units
                result.append(unit_list[u])
        
        return ' '.join(result)
    
    num = int(number)
    result = []
    
    # Миллионы
    millions = num // 1000000
    if millions > 0:
        result.append(convert_below_thousand(millions))
        if millions % 10 == 1 and millions % 100 != 11:
            result.append('миллион')
        elif 2 <= millions % 10 <= 4 and not (11 <= millions % 100 <= 14):
            result.append('миллиона')
        else:
            result.append('миллионов')
    
    # Тысячи
    thousands = (num % 1000000) // 1000
    if thousands > 0:
        result.append(convert_below_thousand(thousands, use_feminine=True))
        if thousands % 10 == 1 and thousands % 100 != 11:
            result.append('тысяча')
        elif 2 <= thousands % 10 <= 4 and not (11 <= thousands % 100 <= 14):
            result.append('тысячи')
        else:
            result.append('тысяч')
    
    # Остаток
    remainder = num % 1000
    if remainder > 0:
        result.append(convert_below_thousand(remainder))
    
    return ' '.join(result).strip() if result else 'ноль'


def generate_invoice_pdf(order, document):
    """Генерирует счёт на оплату по официальному шаблону"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=15*mm, leftMargin=15*mm, 
                            topMargin=10*mm, bottomMargin=15*mm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                   fontName=FONT_NAME, fontSize=9, leading=11)
    
    bold_style = ParagraphStyle('CustomBold', parent=styles['Normal'],
                                 fontName=FONT_NAME_BOLD, fontSize=9, leading=11)
    
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
                                  fontName=FONT_NAME, fontSize=8, leading=10)
    
    # === БАНКОВСКИЕ РЕКВИЗИТЫ (верхняя таблица) ===
    bank_data = [
        [Paragraph(BANK_NAME, normal_style), 
         Paragraph('БИК', bold_style), 
         Paragraph(BANK_BIK, normal_style)],
        ['', 
         Paragraph('Сч. №', bold_style), 
         Paragraph(BANK_CORR_ACCOUNT, normal_style)],
        [Paragraph('Банк получателя', bold_style), '', ''],
        [Paragraph('ИНН ' + COMPANY_INN, normal_style), 
         Paragraph('КПП ' + COMPANY_KPP, normal_style), 
         Paragraph('Сч. №', bold_style)],
        ['', '', Paragraph(BANK_ACCOUNT, normal_style)],
        [Paragraph('Получатель', bold_style), '', ''],
        [Paragraph(COMPANY_NAME, normal_style), '', ''],
    ]
    
    bank_table = Table(bank_data, colWidths=[90*mm, 30*mm, 60*mm])
    bank_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('SPAN', (0, 0), (0, 1)),
        ('SPAN', (1, 0), (2, 0)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (0, 2), (2, 2)),
        ('SPAN', (0, 3), (0, 4)),
        ('SPAN', (1, 3), (1, 4)),
        ('SPAN', (2, 3), (2, 3)),
        ('SPAN', (0, 5), (2, 5)),
        ('SPAN', (0, 6), (2, 6)),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 10*mm))
    
    # === ЗАГОЛОВОК СЧЁТА ===
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
                                  fontName=FONT_NAME_BOLD, fontSize=16, 
                                  alignment=1, spaceAfter=10)
    
    elements.append(Paragraph(f"Счет № {document.document_number} от {document.document_date.strftime('%d.%m.%Y')} г.", title_style))
    elements.append(Spacer(1, 5*mm))
    
    # === ПОСТАВЩИК И ПОКУПАТЕЛЬ ===
    info_data = [
        [Paragraph('<b>Поставщик:</b>', bold_style), 
         Paragraph(f"{COMPANY_NAME}, ИНН {COMPANY_INN}, {COMPANY_ADDRESS}", normal_style)],
        [Paragraph('<b>Покупатель:</b>', bold_style), 
         Paragraph(f"{order.customer.name} {order.customer.surname}, тел.: {order.customer.phone}", normal_style)],
    ]
    
    info_table = Table(info_data, colWidths=[30*mm, 150*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5*mm))
    
    # === ТАБЛИЦА УСЛУГ ===
    product_name = {
        'ring': 'Кольцо',
        'brooch': 'Брошь',
        'bracelet': 'Браслет',
        'earrings': 'Серьги'
    }.get(order.product_type, 'Ювелирное изделие')
    
    order_type_name = {
        'template': 'по шаблону',
        'custom': 'индивидуальное'
    }.get(order.order_type, '')
    
    service_name = f"Изготовление {product_name} {order_type_name}".strip()
    price = order.budget or 0
    
    services_data = [
        [Paragraph('<b>№</b>', bold_style), 
         Paragraph('<b>Наименование работ, услуг</b>', bold_style),
         Paragraph('<b>Кол-во</b>', bold_style),
         Paragraph('<b>Ед.</b>', bold_style),
         Paragraph('<b>Цена</b>', bold_style),
         Paragraph('<b>Сумма</b>', bold_style)],
        [Paragraph('1', normal_style),
         Paragraph(service_name, normal_style),
         Paragraph('1', normal_style),
         Paragraph('шт.', normal_style),
         Paragraph(f'{price:.2f}', normal_style),
         Paragraph(f'{price:.2f}', normal_style)],
    ]
    
    services_table = Table(services_data, colWidths=[10*mm, 80*mm, 20*mm, 15*mm, 30*mm, 30*mm])
    services_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(services_table)
    elements.append(Spacer(1, 3*mm))
    
    # === ИТОГО ===
    total_data = [
        ['', '', '', '', Paragraph('<b>Итого:</b>', bold_style), Paragraph(f'<b>{price:.2f}</b>', bold_style)],
        ['', '', '', '', Paragraph('<b>В том числе НДС:</b>', bold_style), Paragraph('Без НДС', normal_style)],
        ['', '', '', '', Paragraph('<b>Всего к оплате:</b>', bold_style), Paragraph(f'<b>{price:.2f}</b>', bold_style)],
    ]
    
    total_table = Table(total_data, colWidths=[10*mm, 80*mm, 20*mm, 15*mm, 30*mm, 30*mm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('SPAN', (0, 0), (3, 0)),
        ('SPAN', (0, 1), (3, 1)),
        ('SPAN', (0, 2), (3, 2)),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 5*mm))
    
    # === СУММА ПРОПИСЬЮ ===
    rubles = int(price)
    kopeks = int((price - rubles) * 100)
    amount_words = num_to_words_ru(rubles).capitalize()
    
    elements.append(Paragraph(f"Всего наименований 1, на сумму {price:.2f} руб.", normal_style))
    elements.append(Paragraph(f"<b>{amount_words} рублей {kopeks:02d} копеек</b>", bold_style))
    elements.append(Spacer(1, 10*mm))
    
    # === ПОДПИСИ ===
    signature_data = [
        [Paragraph('<b>Руководитель</b>', bold_style), '', Paragraph('__________________', normal_style)],
        [Paragraph('<b>Бухгалтер</b>', bold_style), '', Paragraph('__________________', normal_style)],
    ]
    
    signature_table = Table(signature_data, colWidths=[40*mm, 100*mm, 45*mm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(signature_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_act_pdf(order, document):
    """Генерирует акт оказания услуг по официальному шаблону"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=15*mm, leftMargin=15*mm, 
                            topMargin=15*mm, bottomMargin=15*mm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                   fontName=FONT_NAME, fontSize=10, leading=14)
    
    bold_style = ParagraphStyle('CustomBold', parent=styles['Normal'],
                                 fontName=FONT_NAME_BOLD, fontSize=10, leading=14)
    
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
                                  fontName=FONT_NAME_BOLD, fontSize=14, 
                                  alignment=1, spaceAfter=15)
    
    # === ЗАГОЛОВОК ===
    elements.append(Paragraph(f"Акт № {document.document_number} от «{document.document_date.strftime('%d')}» {document.document_date.strftime('%B')} {document.document_date.year} г.", title_style))
    elements.append(Spacer(1, 10*mm))
    
    # === СТОРОНЫ ===
    elements.append(Paragraph(f"<b>Исполнитель:</b> {COMPANY_NAME}", normal_style))
    elements.append(Paragraph(f"ИНН {COMPANY_INN}, КПП {COMPANY_KPP}, {COMPANY_ADDRESS}", normal_style))
    elements.append(Spacer(1, 5*mm))
    
    elements.append(Paragraph(f"<b>Заказчик:</b> {order.customer.name} {order.customer.surname}", normal_style))
    elements.append(Paragraph(f"Телефон: {order.customer.phone}, Email: {order.customer.email or '—'}", normal_style))
    elements.append(Spacer(1, 5*mm))
    
    elements.append(Paragraph(f"<b>Основание:</b> Заказ №{order.order_id} от {order.created_at.strftime('%d.%m.%Y')}", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # === ТАБЛИЦА УСЛУГ ===
    product_name = {
        'ring': 'Кольцо',
        'brooch': 'Брошь',
        'bracelet': 'Браслет',
        'earrings': 'Серьги'
    }.get(order.product_type, 'Ювелирное изделие')
    
    order_type_name = {
        'template': 'по шаблону',
        'custom': 'индивидуальное'
    }.get(order.order_type, '')
    
    service_name = f"Изготовление {product_name} {order_type_name}".strip()
    price = order.budget or 0
    
    services_data = [
        [Paragraph('<b>№</b>', bold_style), 
         Paragraph('<b>Наименование работ, услуг</b>', bold_style),
         Paragraph('<b>Кол-во</b>', bold_style),
         Paragraph('<b>Ед.</b>', bold_style),
         Paragraph('<b>Цена</b>', bold_style),
         Paragraph('<b>Сумма</b>', bold_style)],
        [Paragraph('1', normal_style),
         Paragraph(service_name, normal_style),
         Paragraph('1', normal_style),
         Paragraph('шт.', normal_style),
         Paragraph(f'{price:.2f}', normal_style),
         Paragraph(f'{price:.2f}', normal_style)],
    ]
    
    services_table = Table(services_data, colWidths=[10*mm, 80*mm, 20*mm, 15*mm, 30*mm, 30*mm])
    services_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(services_table)
    elements.append(Spacer(1, 3*mm))
    
    # === ИТОГО ===
    total_data = [
        ['', '', '', '', Paragraph('<b>Итого:</b>', bold_style), Paragraph(f'<b>{price:.2f}</b>', bold_style)],
        ['', '', '', '', Paragraph('<b>В том числе НДС:</b>', bold_style), Paragraph('Без НДС', normal_style)],
    ]
    
    total_table = Table(total_data, colWidths=[10*mm, 80*mm, 20*mm, 15*mm, 30*mm, 30*mm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('SPAN', (0, 0), (3, 0)),
        ('SPAN', (0, 1), (3, 1)),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 5*mm))
    
    # === СУММА ПРОПИСЬЮ ===
    rubles = int(price)
    kopeks = int((price - rubles) * 100)
    amount_words = num_to_words_ru(rubles).capitalize()
    
    elements.append(Paragraph(f"Всего оказано услуг 1, на сумму {price:.2f} руб.", normal_style))
    elements.append(Paragraph(f"<b>{amount_words} рублей {kopeks:02d} копеек</b>", bold_style))
    elements.append(Spacer(1, 10*mm))
    
    # === ЗАКЛЮЧЕНИЕ ===
    elements.append(Paragraph("Вышеперечисленные услуги выполнены полностью и в срок. Заказчик претензий по объему, качеству и срокам оказания услуг не имеет.", normal_style))
    elements.append(Spacer(1, 15*mm))
    
    # === ПОДПИСИ ===
    signature_data = [
        [Paragraph('<b>ИСПОЛНИТЕЛЬ</b>', bold_style), '', Paragraph('<b>ЗАКАЗЧИК</b>', bold_style)],
        [Paragraph(f'{DIRECTOR_NAME}, {COMPANY_NAME}', normal_style), '', ''],
        ['', '', ''],
        [Paragraph('__________________', normal_style), '', Paragraph('__________________', normal_style)],
        [Paragraph('М.П.', normal_style), '', ''],
    ]
    
    signature_table = Table(signature_data, colWidths=[80*mm, 10*mm, 80*mm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (0, 1), (1, 1)),
    ]))
    elements.append(signature_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_contract_pdf(order, document):
    """Генерирует договор на изготовление изделия"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=20*mm, leftMargin=20*mm, 
                            topMargin=15*mm, bottomMargin=15*mm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                   fontName=FONT_NAME, fontSize=11, leading=15)
    
    bold_style = ParagraphStyle('CustomBold', parent=styles['Normal'],
                                 fontName=FONT_NAME_BOLD, fontSize=11, leading=15)
    
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
                                  fontName=FONT_NAME_BOLD, fontSize=14, 
                                  alignment=1, spaceAfter=20)
    
    # === ЗАГОЛОВОК ===
    elements.append(Paragraph("ДОГОВОР", title_style))
    elements.append(Paragraph(f"на изготовление ювелирного изделия № {document.document_number}", title_style))
    elements.append(Paragraph(f"г. Москва&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{document.document_date.strftime('%d.%m.%Y')} г.", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # === ПРЕАМБУЛА ===
    preamble = f"""
    <b>{COMPANY_NAME}</b> (ИНН {COMPANY_INN}, ОГРН {COMPANY_OGRN}), именуемое в дальнейшем <b>«Исполнитель»</b>, 
    в лице {DIRECTOR_NAME} {DIRECTOR_FIO}, действующего на основании Устава, с одной стороны, 
    и <b>{order.customer.name} {order.customer.surname}</b>, именуемый(ая) в дальнейшем <b>«Заказчик»</b>, 
    с другой стороны, вместе именуемые «Стороны», заключили настоящий Договор о нижеследующем:
    """
    elements.append(Paragraph(preamble, normal_style))
    elements.append(Spacer(1, 7*mm))
    
    # === 1. ПРЕДМЕТ ДОГОВОРА ===
    elements.append(Paragraph("<b>1. ПРЕДМЕТ ДОГОВОРА</b>", bold_style))
    elements.append(Spacer(1, 3*mm))
    
    product_name = {
        'ring': 'кольца',
        'brooch': 'броши',
        'bracelet': 'браслета',
        'earrings': 'серег'
    }.get(order.product_type, 'ювелирного изделия')
    
    subject_text = f"""
    1.1. Исполнитель обязуется изготовить {product_name} (далее – «Изделие») по заказу Заказчика, 
    а Заказчик обязуется принять и оплатить Изделие в порядке и на условиях, предусмотренных настоящим Договором.<br/>
    1.2. Характеристики Изделия:<br/>
    &nbsp;&nbsp;&nbsp;- Тип: {product_name.capitalize()}<br/>
    """
    
    if order.material:
        subject_text += f"&nbsp;&nbsp;&nbsp;- Материал: {order.material}<br/>"
    if order.ring_size:
        subject_text += f"&nbsp;&nbsp;&nbsp;- Размер: {order.ring_size}<br/>"
    
    subject_text += f"""
    1.3. Стоимость работ по изготовлению Изделия составляет <b>{order.budget or 0:.2f} (
    {num_to_words_ru(int(order.budget or 0))} рублей 00 копеек)</b>.
    """
    
    elements.append(Paragraph(subject_text, normal_style))
    elements.append(Spacer(1, 7*mm))
    
    # === 2. СРОКИ ===
    elements.append(Paragraph("<b>2. СРОКИ ВЫПОЛНЕНИЯ РАБОТ</b>", bold_style))
    elements.append(Spacer(1, 3*mm))
    
    deadline_text = f"""
    2.1. Срок изготовления Изделия составляет: {order.required_by.strftime('%d.%m.%Y') if order.required_by else 'согласно индивидуальному графику'}.<br/>
    2.2. Исполнитель обязуется уведомить Заказчика о готовности Изделия по телефону {order.customer.phone}.
    """
    elements.append(Paragraph(deadline_text, normal_style))
    elements.append(Spacer(1, 7*mm))
    
    # === 3. ПОРЯДОК ОПЛАТЫ ===
    elements.append(Paragraph("<b>3. ПОРЯДОК ОПЛАТЫ</b>", bold_style))
    elements.append(Spacer(1, 3*mm))
    
    payment_text = """
    3.1. Заказчик производит предоплату в размере 50% от стоимости работ при подписании настоящего Договора.<br/>
    3.2. Окончательный расчет производится при получении готового Изделия.<br/>
    3.3. Оплата производится наличными денежными средствами либо безналичным переводом на расчетный счет Исполнителя.
    """
    elements.append(Paragraph(payment_text, normal_style))
    elements.append(Spacer(1, 7*mm))
    
    # === 4. ОТВЕТСТВЕННОСТЬ СТОРОН ===
    elements.append(Paragraph("<b>4. ОТВЕТСТВЕННОСТЬ СТОРОН</b>", bold_style))
    elements.append(Spacer(1, 3*mm))
    
    responsibility_text = """
    4.1. За нарушение сроков изготовления Изделия Исполнитель уплачивает Заказчику неустойку в размере 0,1% от стоимости работ за каждый день просрочки.<br/>
    4.2. В случае отказа Заказчика от Изделия после начала работ, предоплата не возвращается.
    """
    elements.append(Paragraph(responsibility_text, normal_style))
    elements.append(Spacer(1, 7*mm))
    
    # === 5. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ ===
    elements.append(Paragraph("<b>5. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</b>", bold_style))
    elements.append(Spacer(1, 3*mm))
    
    final_text = """
    5.1. Настоящий Договор составлен в двух экземплярах, имеющих одинаковую юридическую силу, по одному для каждой из Сторон.<br/>
    5.2. Все изменения и дополнения к настоящему Договору действительны при условии, если они совершены в письменной форме и подписаны обеими Сторонами.
    """
    elements.append(Paragraph(final_text, normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # === РЕКВИЗИТЫ И ПОДПИСИ ===
    elements.append(Paragraph("<b>6. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН</b>", bold_style))
    elements.append(Spacer(1, 5*mm))
    
    details_data = [
        [Paragraph('<b>ИСПОЛНИТЕЛЬ:</b>', bold_style), Paragraph('<b>ЗАКАЗЧИК:</b>', bold_style)],
        [Paragraph(f'{COMPANY_NAME}<br/>ИНН: {COMPANY_INN}<br/>КПП: {COMPANY_KPP}<br/>Адрес: {COMPANY_ADDRESS}<br/>Тел.: {COMPANY_PHONE}', normal_style),
         Paragraph(f'{order.customer.name} {order.customer.surname}<br/>Телефон: {order.customer.phone}<br/>Email: {order.customer.email or "—"}', normal_style)],
        ['', ''],
        [Paragraph(f'_______________ {DIRECTOR_FIO}', normal_style), Paragraph('_______________', normal_style)],
        [Paragraph('М.П.', normal_style), ''],
    ]
    
    details_table = Table(details_data, colWidths=[85*mm, 85*mm])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(details_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
