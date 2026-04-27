"""
Inventory app admin configuration.
"""

from django.contrib import admin
from .models import Item, StockMovement, PriceChange

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'buying_price', 'selling_price', 'current_stock', 'status']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['code', 'created_at', 'updated_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity_change', 'reason', 'performed_by', 'timestamp']
    list_filter = ['reason', 'timestamp']
    search_fields = ['item__name']

@admin.register(PriceChange)
class PriceChangeAdmin(admin.ModelAdmin):
    list_display = ['item', 'price_type', 'old_price', 'new_price', 'changed_by', 'timestamp']
    list_filter = ['price_type', 'timestamp']
    search_fields = ['item__name']
