"""
Inventory app URLs.
"""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('adjust-stock/', views.adjust_stock, name='adjust_stock'),
    path('autocomplete/', views.item_autocomplete, name='item_autocomplete'),
    path('price-management/', views.price_management, name='price_management'),
    path('price-history/', views.price_history, name='price_history'),
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
]
