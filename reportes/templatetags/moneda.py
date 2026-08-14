from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format a numeric value as currency with thousands separator and two decimals.

    Example: 1234.5 -> $ 1,234.50
    """
    try:
        val = Decimal(value)
    except (TypeError, InvalidOperation):
        return ''
    # Use Python formatting with comma as thousand separator
    return f"$ {val:,.2f}"
