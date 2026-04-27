#!/usr/bin/env python
"""
Populate inventory with sample data for Luanda Feeds Centre.
Run this script after migrations to add initial inventory items.
"""

import os
import sys
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luanda_feeds.settings')
django.setup()

from decimal import Decimal
from users.models import User
from inventory.models import Item, StockMovement

def create_users():
    """Create default users for the system."""
    users_data = [
        {
            'username': 'manager',
            'email': 'manager@luandafeeds.co.ke',
            'password': 'manager123',
            'first_name': 'John',
            'last_name': 'Manager',
            'role': 'manager',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'cashier1',
            'email': 'cashier1@luandafeeds.co.ke',
            'password': 'cashier123',
            'first_name': 'Mary',
            'last_name': 'Cashier',
            'role': 'cashier',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'inventory',
            'email': 'inventory@luandafeeds.co.ke',
            'password': 'inventory123',
            'first_name': 'Peter',
            'last_name': 'Inventory',
            'role': 'inventory',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'admin',
            'email': 'admin@luandafeeds.co.ke',
            'password': 'admin123',
            'first_name': 'System',
            'last_name': 'Admin',
            'role': 'manager',
            'is_staff': True,
            'is_superuser': True,
        },
    ]

    for user_data in users_data:
        password = user_data.pop('password')
        username = user_data['username']

        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")

def create_inventory():
    """Create sample inventory items."""
    inventory_data = [
        # Poultry Feeds
        {
            'name': 'Fugo Growers Mash 50KG',
            'buying_price': Decimal('2800.00'),
            'selling_price': Decimal('3200.00'),
            'current_stock': Decimal('150'),
            'category': 'Poultry Feed',
            'low_stock_threshold': Decimal('20'),
        },
        {
            'name': 'Fugo Layers Mash 50KG',
            'buying_price': Decimal('3000.00'),
            'selling_price': Decimal('3400.00'),
            'current_stock': Decimal('120'),
            'category': 'Poultry Feed',
            'low_stock_threshold': Decimal('25'),
        },
        {
            'name': 'Fugo Broiler Starter 50KG',
            'buying_price': Decimal('3200.00'),
            'selling_price': Decimal('3700.00'),
            'current_stock': Decimal('80'),
            'category': 'Poultry Feed',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Fugo Broiler Finisher 50KG',
            'buying_price': Decimal('3100.00'),
            'selling_price': Decimal('3600.00'),
            'current_stock': Decimal('100'),
            'category': 'Poultry Feed',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Kenchic Starter Mash 50KG',
            'buying_price': Decimal('2900.00'),
            'selling_price': Decimal('3300.00'),
            'current_stock': Decimal('60'),
            'category': 'Poultry Feed',
            'low_stock_threshold': Decimal('10'),
        },

        # Dairy Feeds
        {
            'name': 'Dairy Meal 50KG',
            'buying_price': Decimal('3500.00'),
            'selling_price': Decimal('4000.00'),
            'current_stock': Decimal('200'),
            'category': 'Dairy Feed',
            'low_stock_threshold': Decimal('30'),
        },
        {
            'name': 'Dairy Concentrate 40KG',
            'buying_price': Decimal('4200.00'),
            'selling_price': Decimal('4800.00'),
            'current_stock': Decimal('50'),
            'category': 'Dairy Feed',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Mineral Lick Block 10KG',
            'buying_price': Decimal('1200.00'),
            'selling_price': Decimal('1500.00'),
            'current_stock': Decimal('100'),
            'category': 'Dairy Feed',
            'low_stock_threshold': Decimal('20'),
        },

        # Livestock Feeds
        {
            'name': 'Pig Grower 50KG',
            'buying_price': Decimal('2600.00'),
            'selling_price': Decimal('3000.00'),
            'current_stock': Decimal('90'),
            'category': 'Livestock Feed',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Pig Finisher 50KG',
            'buying_price': Decimal('2500.00'),
            'selling_price': Decimal('2900.00'),
            'current_stock': Decimal('85'),
            'category': 'Livestock Feed',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Rabbit Pellets 25KG',
            'buying_price': Decimal('1400.00'),
            'selling_price': Decimal('1700.00'),
            'current_stock': Decimal('45'),
            'category': 'Livestock Feed',
            'low_stock_threshold': Decimal('10'),
        },

        # Fish Feeds
        {
            'name': 'Fish Feed Floating 25KG',
            'buying_price': Decimal('3800.00'),
            'selling_price': Decimal('4500.00'),
            'current_stock': Decimal('30'),
            'category': 'Fish Feed',
            'low_stock_threshold': Decimal('8'),
        },
        {
            'name': 'Fish Feed Sinking 25KG',
            'buying_price': Decimal('3500.00'),
            'selling_price': Decimal('4200.00'),
            'current_stock': Decimal('25'),
            'category': 'Fish Feed',
            'low_stock_threshold': Decimal('5'),
        },

        # Supplements & Additives
        {
            'name': 'Vitamin Premix 1KG',
            'buying_price': Decimal('800.00'),
            'selling_price': Decimal('1100.00'),
            'current_stock': Decimal('50'),
            'category': 'Supplements',
            'low_stock_threshold': Decimal('10'),
        },
        {
            'name': 'Probiotics 500G',
            'buying_price': Decimal('600.00'),
            'selling_price': Decimal('850.00'),
            'current_stock': Decimal('35'),
            'category': 'Supplements',
            'low_stock_threshold': Decimal('8'),
        },
        {
            'name': 'Shell Grit 50KG',
            'buying_price': Decimal('800.00'),
            'selling_price': Decimal('1200.00'),
            'current_stock': Decimal('80'),
            'category': 'Supplements',
            'low_stock_threshold': Decimal('15'),
        },

        # Fertilizers
        {
            'name': 'CAN Fertilizer 50KG',
            'buying_price': Decimal('2200.00'),
            'selling_price': Decimal('2800.00'),
            'current_stock': Decimal('120'),
            'category': 'Fertilizer',
            'low_stock_threshold': Decimal('25'),
        },
        {
            'name': 'DAP Fertilizer 50KG',
            'buying_price': Decimal('2800.00'),
            'selling_price': Decimal('3500.00'),
            'current_stock': Decimal('100'),
            'category': 'Fertilizer',
            'low_stock_threshold': Decimal('20'),
        },
        {
            'name': 'NPK Fertilizer 50KG',
            'buying_price': Decimal('2500.00'),
            'selling_price': Decimal('3200.00'),
            'current_stock': Decimal('90'),
            'category': 'Fertilizer',
            'low_stock_threshold': Decimal('20'),
        },

        # Vaccines & Medications
        {
            'name': 'Newcastle Vaccine 1000 Doses',
            'buying_price': Decimal('1500.00'),
            'selling_price': Decimal('2000.00'),
            'current_stock': Decimal('40'),
            'category': 'Veterinary',
            'low_stock_threshold': Decimal('10'),
        },
        {
            'name': 'Gumboro Vaccine 1000 Doses',
            'buying_price': Decimal('1800.00'),
            'selling_price': Decimal('2400.00'),
            'current_stock': Decimal('30'),
            'category': 'Veterinary',
            'low_stock_threshold': Decimal('8'),
        },
        {
            'name': 'Dewormer 1L',
            'buying_price': Decimal('900.00'),
            'selling_price': Decimal('1300.00'),
            'current_stock': Decimal('55'),
            'category': 'Veterinary',
            'low_stock_threshold': Decimal('12'),
        },
        {
            'name': 'Antibiotic Injection 100ML',
            'buying_price': Decimal('1200.00'),
            'selling_price': Decimal('1600.00'),
            'current_stock': Decimal('45'),
            'category': 'Veterinary',
            'low_stock_threshold': Decimal('10'),
        },

        # Equipment
        {
            'name': 'Chicken Feeder 5KG',
            'buying_price': Decimal('450.00'),
            'selling_price': Decimal('650.00'),
            'current_stock': Decimal('60'),
            'category': 'Equipment',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Chicken Drinker 5L',
            'buying_price': Decimal('350.00'),
            'selling_price': Decimal('500.00'),
            'current_stock': Decimal('70'),
            'category': 'Equipment',
            'low_stock_threshold': Decimal('15'),
        },
        {
            'name': 'Poultry Incubator 50 Eggs',
            'buying_price': Decimal('8500.00'),
            'selling_price': Decimal('11000.00'),
            'current_stock': Decimal('8'),
            'category': 'Equipment',
            'low_stock_threshold': Decimal('2'),
        },
        {
            'name': 'Water Trough 50L',
            'buying_price': Decimal('1200.00'),
            'selling_price': Decimal('1600.00'),
            'current_stock': Decimal('25'),
            'category': 'Equipment',
            'low_stock_threshold': Decimal('5'),
        },
    ]

    for item_data in inventory_data:
        item, created = Item.objects.get_or_create(
            name=item_data['name'],
            defaults=item_data
        )
        if created:
            print(f"Created item: {item_data['name']}")

            # Create initial stock movement
            if item_data['current_stock'] > 0:
                StockMovement.objects.create(
                    item=item,
                    quantity_change=item_data['current_stock'],
                    reason='Delivery',
                    notes='Initial stock from populate script',
                    performed_by=User.objects.filter(is_superuser=True).first()
                )
        else:
            print(f"Item already exists: {item_data['name']}")

def main():
    """Main function to populate database."""
    print("=" * 50)
    print("Luanda Feeds Centre - Populating Database")
    print("=" * 50)

    print("\nCreating users...")
    create_users()

    print("\nCreating inventory items...")
    create_inventory()

    print("\n" + "=" * 50)
    print("Database population complete!")
    print("=" * 50)
    print("\nDefault users created:")
    print("  - admin / admin123 (Superuser)")
    print("  - manager / manager123 (Manager)")
    print("  - cashier1 / cashier123 (Cashier)")
    print("  - inventory / inventory123 (Inventory Manager)")

if __name__ == '__main__':
    main()
