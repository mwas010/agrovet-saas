"""
Sales models: Sale, SaleItem.
"""

from django.db import models
from django.conf import settings
from inventory.models import Item

class Sale(models.Model):
    """Represents a complete sales transaction."""

    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    change_given = models.DecimalField(max_digits=12, decimal_places=2)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

    def __str__(self):
        return f"{self.transaction_id} - {self.employee} - {self.timestamp}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        """Generate unique transaction ID: SALES-YYYYMMDD-XXXX"""
        from django.utils import timezone
        from datetime import datetime

        today = timezone.now().strftime('%Y%m%d')
        prefix = f"SALES-{today}-"

        # Find last transaction for today
        last_today = Sale.objects.filter(
            transaction_id__startswith=prefix
        ).order_by('-transaction_id').first()

        if last_today:
            last_num = int(last_today.transaction_id.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @property
    def items_count(self):
        return self.items.count()


class SaleItem(models.Model):
    """Individual item in a sale (snapshots prices)."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=255)  # Snapshot of item name
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    buying_price = models.DecimalField(max_digits=12, decimal_places=2)  # Snapshot
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)  # Snapshot
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate line total
        self.line_total = self.quantity * self.selling_price

        # Snap item name if not set
        if not self.item_name and self.item:
            self.item_name = self.item.name

        super().save(*args, **kwargs)
