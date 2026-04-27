"""
Inventory app views for item management and dashboard.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Item, StockMovement, PriceChange
from sales.models import Sale, SaleItem

@login_required
def inventory_list(request):
    """List all items in inventory with search and filters."""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    items = Item.objects.all()

    if search_query:
        items = items.filter(name__icontains=search_query)

    if category_filter:
        items = items.filter(category=category_filter)

    # Get unique categories for filter dropdown
    categories = Item.objects.exclude(category='').values_list('category', flat=True).distinct()

    # Highlight low stock items
    low_stock_items = Item.objects.filter(
        current_stock__lte=F('low_stock_threshold')
    ).values_list('id', flat=True)

    context = {
        'items': items,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'low_stock_items': list(low_stock_items),
    }
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def add_item(request):
    """Add a new item to inventory."""
    if not request.user.can_manage_inventory():
        messages.error(request, 'You do not have permission to add items.')
        return redirect('inventory:inventory_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        buying_price = request.POST.get('buying_price')
        selling_price = request.POST.get('selling_price')
        current_stock = request.POST.get('current_stock', 0)
        category = request.POST.get('category', '')
        low_stock_threshold = request.POST.get('low_stock_threshold', 0)

        # Check if item name already exists
        if Item.objects.filter(name__iexact=name).exists():
            messages.error(request, f'An item with name "{name}" already exists.')
            return render(request, 'inventory/add_item.html')

        try:
            item = Item.objects.create(
                name=name,
                buying_price=Decimal(buying_price),
                selling_price=Decimal(selling_price),
                current_stock=Decimal(current_stock),
                category=category,
                low_stock_threshold=Decimal(low_stock_threshold)
            )

            # Log stock movement if initial stock > 0
            if Decimal(current_stock) > 0:
                StockMovement.objects.create(
                    item=item,
                    quantity_change=Decimal(current_stock),
                    reason='Delivery',
                    notes='Initial stock',
                    performed_by=request.user
                )

            messages.success(request, f'Item "{item.name}" added successfully.')
            return redirect('inventory:inventory_list')
        except Exception as e:
            messages.error(request, f'Error adding item: {str(e)}')

    return render(request, 'inventory/add_item.html')

@login_required
def edit_item(request, pk):
    """Edit an existing item."""
    if not request.user.can_manage_inventory():
        messages.error(request, 'You do not have permission to edit items.')
        return redirect('inventory:inventory_list')

    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        item.name = request.POST.get('name')

        # Track price changes
        new_buying_price = Decimal(request.POST.get('buying_price'))
        new_selling_price = Decimal(request.POST.get('selling_price'))

        if item.buying_price != new_buying_price:
            PriceChange.objects.create(
                item=item,
                price_type='buying',
                old_price=item.buying_price,
                new_price=new_buying_price,
                changed_by=request.user
            )
            item.buying_price = new_buying_price

        if item.selling_price != new_selling_price:
            PriceChange.objects.create(
                item=item,
                price_type='selling',
                old_price=item.selling_price,
                new_price=new_selling_price,
                changed_by=request.user
            )
            item.selling_price = new_selling_price

        item.current_stock = Decimal(request.POST.get('current_stock'))
        item.category = request.POST.get('category', '')
        item.low_stock_threshold = Decimal(request.POST.get('low_stock_threshold', 0))
        item.save()

        messages.success(request, f'Item "{item.name}" updated successfully.')
        return redirect('inventory:inventory_list')

    return render(request, 'inventory/edit_item.html', {'item': item})

@login_required
@require_http_methods(["POST"])
def delete_item(request, pk):
    """Delete an item from inventory."""
    if not request.user.can_manage_inventory():
        messages.error(request, 'You do not have permission to delete items.')
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    item = get_object_or_404(Item, pk=pk)
    item_name = item.name
    item.delete()

    messages.success(request, f'Item "{item_name}" deleted successfully.')
    return JsonResponse({'success': True})

@login_required
def adjust_stock(request):
    """Adjust stock levels (add or reduce)."""
    if not request.user.can_manage_inventory():
        messages.error(request, 'You do not have permission to adjust stock.')
        return redirect('inventory:inventory_list')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')
        notes = request.POST.get('notes', '')

        if not all([item_id, quantity, reason]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'inventory/adjust_stock.html')

        try:
            item = Item.objects.get(pk=item_id)
            quantity_decimal = Decimal(quantity)

            if quantity_decimal == 0:
                messages.error(request, 'Quantity cannot be zero.')
                return render(request, 'inventory/adjust_stock.html')

            StockMovement.objects.create(
                item=item,
                quantity_change=quantity_decimal,
                reason=reason,
                notes=notes,
                performed_by=request.user
            )

            messages.success(request, f'Stock for "{item.name}" adjusted by {quantity_decimal:+}.')
            return redirect('inventory:inventory_list')
        except Item.DoesNotExist:
            messages.error(request, 'Item not found.')
        except Exception as e:
            messages.error(request, f'Error adjusting stock: {str(e)}')

    return render(request, 'inventory/adjust_stock.html')

@login_required
def item_autocomplete(request):
    """Autocomplete search for items."""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'results': []})

    items = Item.objects.filter(name__icontains=query).values(
        'id', 'name', 'selling_price', 'current_stock'
    )[:10]

    results = [
        {
            'id': item['id'],
            'name': item['name'],
            'price': float(item['selling_price']),
            'stock': float(item['current_stock'])
        }
        for item in items
    ]

    return JsonResponse({'results': results})

@login_required
def price_management(request):
    """Update buying or selling prices for items."""
    if not request.user.can_manage_prices():
        messages.error(request, 'You do not have permission to manage prices.')
        return redirect('inventory:manager_dashboard')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        price_type = request.POST.get('price_type')
        new_price = request.POST.get('new_price')

        if not all([item_id, price_type, new_price]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'inventory/price_management.html')

        try:
            item = Item.objects.get(pk=item_id)
            new_price_decimal = Decimal(new_price)

            if price_type == 'buying':
                old_price = item.buying_price
                item.buying_price = new_price_decimal
            else:
                old_price = item.selling_price
                item.selling_price = new_price_decimal

            # Log price change
            PriceChange.objects.create(
                item=item,
                price_type=price_type,
                old_price=old_price,
                new_price=new_price_decimal,
                changed_by=request.user
            )

            item.save()
            messages.success(request, f'{price_type.capitalize()} price for "{item.name}" updated to {new_price_decimal}.')
            return redirect('inventory:price_management')
        except Item.DoesNotExist:
            messages.error(request, 'Item not found.')
        except Exception as e:
            messages.error(request, f'Error updating price: {str(e)}')

    return render(request, 'inventory/price_management.html')

@login_required
def price_history(request):
    """View full price change history."""
    if not request.user.can_manage_prices():
        messages.error(request, 'You do not have permission to view price history.')
        return redirect('inventory:manager_dashboard')

    changes = PriceChange.objects.select_related('item', 'changed_by').all()

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page

    total_pages = (changes.count() + per_page - 1) // per_page
    changes = changes[start:end]

    context = {
        'changes': changes,
        'page': page,
        'total_pages': total_pages,
    }
    return render(request, 'inventory/price_history.html', context)

@login_required
def manager_dashboard(request):
    """Manager dashboard with analytics and overview."""
    if not request.user.can_view_reports():
        messages.error(request, 'You do not have permission to view the manager dashboard.')
        return redirect('sales:cashier_dashboard')

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Top cards data
    today_transactions = Sale.objects.filter(timestamp__gte=today_start).count()
    today_revenue = Sale.objects.filter(timestamp__gte=today_start).aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    low_stock_count = Item.objects.filter(
        current_stock__lte=F('low_stock_threshold')
    ).count()

    # Low stock items (sorted by most urgent)
    low_stock_items = Item.objects.filter(
        current_stock__lte=F('low_stock_threshold')
    ).order_by('current_stock')[:10]

    # Top selling items this week
    week_ago = now - timedelta(days=7)
    top_selling = SaleItem.objects.filter(
        sale__timestamp__gte=week_ago
    ).values('item__name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]

    # Recent stock movements
    recent_movements = StockMovement.objects.select_related(
        'item', 'performed_by'
    ).order_by('-timestamp')[:10]

    # Recent price changes
    recent_price_changes = PriceChange.objects.select_related(
        'item', 'changed_by'
    ).order_by('-timestamp')[:7]

    context = {
        'today_transactions': today_transactions,
        'today_revenue': today_revenue,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items,
        'top_selling': top_selling,
        'recent_movements': recent_movements,
        'recent_price_changes': recent_price_changes,
    }
    return render(request, 'inventory/manager_dashboard.html', context)
