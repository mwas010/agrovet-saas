"""
Sales app URLs.
"""

from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('pos/', views.pos, name='pos'),
    path('checkout/', views.checkout, name='checkout'),
    path('receipt/<str:transaction_id>/', views.receipt, name='receipt'),
    path('cashier-dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('get-item/<int:item_id>/', views.get_item, name='get_item'),
    path('search-items/', views.search_items, name='search_items'),
]
