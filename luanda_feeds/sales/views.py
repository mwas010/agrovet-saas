"""
Sales app views for POS and transactions.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from inventory.models import Item, StockMovement
from .models import Sale, SaleItem

@login_required
def search_items(request):
    """Search items for POS autocomplete."""
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'results': []})

    items = Item.objects.filter(
        name__icontains=query,
        current_stock__gt=0
    ).values(
        'id', 'name', 'selling_price', 'current_stock'
    )[:10]

    results = [
        {
            'id': item['id'],
            'text': f"{item['name']} - KES {item['selling_price']} (Stock: {item['current_stock']})",
            'name': item['name'],
            'price': float(item['selling_price']),
            'stock': float(item['current_stock'])
        }
        for item in items
    ]

    return JsonResponse({'results': results})

@login_required
def get_item(request, item_id):
    """Get item details for POS."""
    try:
        item = Item.objects.get(pk=item_id)
        return JsonResponse({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'selling_price': float(item.selling_price),
                'current_stock': float(item.current_stock),
                'in_stock': item.current_stock > 0
            }
        })
    except Item.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

@login_required
def pos(request):
    """Point of Sale interface."""
    return render(request, 'sales/pos.html')

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def checkout(request):
    """Process checkout and create sale."""
    cart_data = request.POST.get('cart_data')
    amount_paid = request.POST.get('amount_paid')

    if not cart_data or not amount_paid:
        return JsonResponse({'success': False, 'error': 'Missing data'})

    try:
        import json
        cart = json.loads(cart_data)
        amount_paid_decimal = Decimal(amount_paid)

        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty'})

        # Calculate total
        total = Decimal('0')
        for item_data in cart:
            item_id = item_data.get('id')
            quantity = Decimal(str(item_data.get('quantity', 1)))

            try:
                item = Item.objects.select_for_update().get(pk=item_id)
            except Item.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'Item not found: {item_id}'})

            # Check stock
            if item.current_stock < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Insufficient stock for {item.name}. Available: {item.current_stock}'
                })

            total += item.selling_price * quantity

        # Check amount paid
        if amount_paid_decimal < total:
            return JsonResponse({
                'success': False,
                'error': f'Amount paid (KES {amount_paid_decimal}) is less than total (KES {total})'
            })

        change = amount_paid_decimal - total

        # Create sale
        sale = Sale.objects.create(
            total_amount=total,
            amount_paid=amount_paid_decimal,
            change_given=change,
            employee=request.user
        )

        # Create sale items and update stock
        for item_data in cart:
            item_id = item_data.get('id')
            quantity = Decimal(str(item_data.get('quantity', 1)))

            item = Item.objects.select_for_update().get(pk=item_id)

            # Create sale item with snapped prices
            SaleItem.objects.create(
                sale=sale,
                item=item,
                item_name=item.name,
                quantity=quantity,
                buying_price=item.buying_price,
                selling_price=item.selling_price
            )

            # Deduct stock
            item.current_stock -= quantity
            item.save()

            # Log stock movement
            StockMovement.objects.create(
                item=item,
                quantity_change=-quantity,
                reason='Sale',
                notes=f'Transaction: {sale.transaction_id}',
                performed_by=request.user
            )

        return JsonResponse({
            'success': True,
            'transaction_id': sale.transaction_id,
            'total': str(total),
            'change': str(change)
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid cart data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def receipt(request, transaction_id):
    """View and print receipt."""
    try:
        sale = Sale.objects.select_related('employee').prefetch_related('items').get(
            transaction_id=transaction_id
        )
    except Sale.DoesNotExist:
        messages.error(request, 'Transaction not found.')
        return redirect('sales:cashier_dashboard')

    context = {
        'sale': sale,
        'items': sale.items.all(),
    }
    return render(request, 'sales/receipt.html', context)

@login_required
def cashier_dashboard(request):
    """Cashier dashboard with today's transactions."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Today's transactions
    today_transactions = Sale.objects.filter(
        timestamp__gte=today_start,
        employee=request.user
    ).count()

    # Last 5 transactions
    last_transactions = Sale.objects.filter(
        employee=request.user
    ).select_related('employee').prefetch_related('items').order_by('-timestamp')[:5]

    context = {
        'today_transactions': today_transactions,
        'last_transactions': last_transactions,
    }
    return render(request, 'sales/cashier_dashboard.html', context)
