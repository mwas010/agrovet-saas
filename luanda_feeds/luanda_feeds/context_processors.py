"""
Luanda Feeds Centre - Agrovet Automation Software
Context processors for global variables.
"""

def currency(request):
    """Inject currency symbol into all templates."""
    from django.conf import settings
    return {'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', 'KES')}
