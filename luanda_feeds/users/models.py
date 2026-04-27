"""
Custom User model with role-based access control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with roles for Luanda Feeds Centre."""

    ROLE_CHOICES = [
        ('cashier', 'Cashier'),
        ('inventory', 'Inventory Manager'),
        ('manager', 'Manager'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def is_cashier(self):
        return self.role == 'cashier'

    def is_inventory_manager(self):
        return self.role == 'inventory'

    def is_manager(self):
        return self.role == 'manager' or self.is_superuser

    def can_manage_inventory(self):
        return self.role in ['inventory', 'manager'] or self.is_superuser

    def can_manage_users(self):
        return self.is_manager()

    def can_manage_prices(self):
        return self.is_manager()

    def can_view_reports(self):
        return self.is_manager()
