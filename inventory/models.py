"""
Inventory models: Item, StockMovement, PriceChange.
"""

from django.db import models
from django.conf import settings

class Item(models.Model):
    """
    Product item in the inventory.
    Code is auto-generated from name.
    """

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=100, unique=True, editable=False, blank=True)
    buying_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    category = models.CharField(max_length=100, blank=True, default='')
    low_stock_threshold = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        """Generate a unique code from the item name."""
        # Create base code from name (uppercase, spaces to hyphens)
        base = ''.join(c.upper() for c in self.name if c.isalnum() or c == ' ')
        base = '-'.join(base.split())

        # Add random suffix for uniqueness
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_uppercase, k=4))

        return f"{base[:30]}-{suffix}"

    def is_low_stock(self):
        """Check if item is below low stock threshold."""
        return self.current_stock <= self.low_stock_threshold

    @property
    def status(self):
        """Return stock status."""
        return 'Low Stock' if self.is_low_stock() else 'OK'


class StockMovement(models.Model):
    """
    Track all stock changes (sales, adjustments, deliveries).
    """

    REASON_CHOICES = [
        ('Sale', 'Sale'),
        ('Delivery', 'New Delivery'),
        ('Adjustment', 'Stock Adjustment'),
        ('Spoilage', 'Spoilage/Damage'),
        ('Return', 'Customer Return'),
        ('Other', 'Other'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='movements')
    quantity_change = models.DecimalField(max_digits=14, decimal_places=3)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    notes = models.TextField(blank=True, default='')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'

    def __str__(self):
        sign = '+' if self.quantity_change > 0 else ''
        return f"{self.item.name}: {sign}{self.quantity_change} ({self.reason})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only update stock on new records
            Item.objects.filter(pk=self.item.pk).update(
                current_stock=models.F('current_stock') + self.quantity_change
            )
        super().save(*args, **kwargs)


class PriceChange(models.Model):
    """
    Track all price changes for audit.
    """

    PRICE_TYPE_CHOICES = [
        ('buying', 'Buying Price'),
        ('selling', 'Selling Price'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='price_changes')
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Price Change'
        verbose_name_plural = 'Price Changes'

    def __str__(self):
        return f"{self.item.name}: {self.price_type} changed from {self.old_price} to {self.new_price}"
