from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Accounts (аутентификация)
    path('', accounts_views.home_view, name='home'),
    path('register/', accounts_views.register, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    
    # НОВЫЕ ПУТИ: Управление клиентами (для менеджера)
    path('customers/', accounts_views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/orders/', accounts_views.customer_orders, name='customer_orders'),
    
    # Orders
    path('orders/', include('orders.urls')),
    
    path('catalog/', include('catalog.urls')),
]
