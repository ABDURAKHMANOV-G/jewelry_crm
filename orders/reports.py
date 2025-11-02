from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from django.db.models import Count, Sum, Q
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

# Компания
COMPANY_NAME = "ООО «JEWEllUX»"


def generate_report_data(orders):
    """Собирает аналитические данные"""
    
    # Общая статистика
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('budget'))['total'] or 0
    
    # По статусам
    status_stats = orders.values('order_status').annotate(count=Count('order_id')).order_by('-count')
    
    # По типам изделий
    product_stats = orders.values('product_type').annotate(count=Count('order_id')).order_by('-count')
    
    # По типам заказов
    order_type_stats = orders.values('order_type').annotate(count=Count('order_id')).order_by('-count')
    
    # Топ-5 клиентов по количеству заказов
    top_customers = orders.values('customer__name', 'customer__surname').annotate(
        count=Count('order_id'),
        total_spent=Sum('budget')
    ).order_by('-count')[:5]
    
    # Средний чек
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'status_stats': status_stats,
        'product_stats': product_stats,
        'order_type_stats': order_type_stats,
        'top_customers': top_customers,
    }


def generate_report_pdf(start_date, end_date, report_data):
    """Генерирует PDF-отчёт"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14
    )
    
    # Заголовок
    elements.append(Paragraph(f"ОТЧЁТ О РАБОТЕ КОМПАНИИ", title_style))
    elements.append(Paragraph(COMPANY_NAME, normal_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Период
    period_text = f"<b>Период:</b> {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
    elements.append(Paragraph(period_text, normal_style))
    elements.append(Paragraph(f"<b>Дата формирования отчёта:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== ОБЩАЯ СТАТИСТИКА =====
    elements.append(Paragraph("📊 ОБЩАЯ СТАТИСТИКА", heading_style))
    
    general_stats = [
        ['Показатель', 'Значение'],
        ['Всего заказов', str(report_data['total_orders'])],
        ['Общая выручка', f"{report_data['total_revenue']:.2f} ₽"],
        ['Средний чек', f"{report_data['avg_order_value']:.2f} ₽"],
    ]
    
    general_table = Table(general_stats, colWidths=[8*cm, 6*cm])
    general_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
    ]))
    elements.append(general_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== СТАТИСТИКА ПО СТАТУСАМ =====
    elements.append(Paragraph("📋 ЗАКАЗЫ ПО СТАТУСАМ", heading_style))
    
    status_names = {
        'new': 'Новый',
        'confirmed': 'Подтверждён',
        'in_work': 'В работе',
        'ready': 'Готов',
        'delivered': 'Доставлен',
    }
    
    status_data = [['Статус', 'Количество']]
    for item in report_data['status_stats']:
        status_name = status_names.get(item['order_status'], item['order_status'])
        status_data.append([status_name, str(item['count'])])
    
    status_table = Table(status_data, colWidths=[8*cm, 6*cm])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== СТАТИСТИКА ПО ИЗДЕЛИЯМ =====
    elements.append(Paragraph("💍 ТИПЫ ИЗДЕЛИЙ", heading_style))
    
    product_names = {
        'ring': 'Кольца',
        'brooch': 'Броши',
        'bracelet': 'Браслеты',
        'earrings': 'Серьги',
    }
    
    product_data = [['Тип изделия', 'Количество']]
    for item in report_data['product_stats']:
        product_name = product_names.get(item['product_type'], item['product_type'] or 'Не указано')
        product_data.append([product_name, str(item['count'])])
    
    product_table = Table(product_data, colWidths=[8*cm, 6*cm])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(product_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== ТОП КЛИЕНТОВ =====
    elements.append(Paragraph("👥 ТОП-5 КЛИЕНТОВ", heading_style))
    
    customer_data = [['Клиент', 'Заказов', 'Сумма']]
    for customer in report_data['top_customers']:
        name = f"{customer['customer__name']} {customer['customer__surname']}"
        count = str(customer['count'])
        total = f"{customer['total_spent'] or 0:.2f} ₽"
        customer_data.append([name, count, total])
    
    customer_table = Table(customer_data, colWidths=[7*cm, 3*cm, 4*cm])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(customer_table)
    
    # Подвал
    elements.append(Spacer(1, 1*cm))
    footer_text = f"<i>Отчёт сформирован автоматически системой CRM {COMPANY_NAME}</i>"
    elements.append(Paragraph(footer_text, normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
