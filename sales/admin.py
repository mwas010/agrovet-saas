"""
Sales app admin configuration.
"""

from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['item', 'item_name', 'quantity', 'buying_price', 'selling_price', 'line_total']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'employee', 'timestamp', 'total_amount', 'amount_paid', 'change_given']
    list_filter = ['timestamp', 'employee']
    search_fields = ['transaction_id']
    inlines = [SaleItemInline]
    readonly_fields = ['transaction_id', 'timestamp']

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'item_name', 'quantity', 'selling_price', 'line_total']
    list_filter = ['sale__timestamp']
