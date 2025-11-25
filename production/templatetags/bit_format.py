"""
Template filters for bit design display formatting
"""

from django import template
from decimal import Decimal

register = template.Library()

# Bit size mapping: decimal values to fraction labels
BIT_SIZE_MAP = {
    Decimal("3.625"): '3 5/8"',
    Decimal("3.75"): '3 3/4"',
    Decimal("3.875"): '3 7/8"',
    Decimal("5.5"): '5 1/2"',
    Decimal("5.875"): '5 7/8"',
    Decimal("6"): '6"',
    Decimal("6.125"): '6 1/8"',
    Decimal("6.25"): '6 1/4"',
    Decimal("8.375"): '8 3/8"',
    Decimal("8.5"): '8 1/2"',
    Decimal("12"): '12"',
    Decimal("12.25"): '12 1/4"',
    Decimal("14.5"): '14 1/2"',
    Decimal("16"): '16"',
    Decimal("17"): '17"',
    Decimal("17.5"): '17 1/2"',
    Decimal("22"): '22"',
    Decimal("24"): '24"',
    Decimal("27"): '27"',
    Decimal("28"): '28"',
    Decimal("34"): '34"',
}


@register.filter
def bit_size_display(value):
    """
    Display bit size with fraction labels

    Examples:
        8.5 → 8 1/2"
        12.25 → 12 1/4"
        17 → 17"
    """
    if not value:
        return "—"

    try:
        dec_val = Decimal(str(value))
        # Try to find exact match in map
        if dec_val in BIT_SIZE_MAP:
            return BIT_SIZE_MAP[dec_val]
        # Otherwise format as decimal with quotes
        return f'{float(dec_val):.2f}"'.rstrip('0').rstrip('.') + '"'
    except (ValueError, TypeError):
        return str(value)


@register.filter
def length_display(value):
    """
    Display length cleanly (no unnecessary decimals)

    Examples:
        2.500 → 2.5
        3.000 → 3
        1.250 → 1.25
    """
    if not value:
        return "—"

    try:
        fval = float(value)
        # If it's a whole number, show as integer
        if fval == int(fval):
            return str(int(fval))
        # Otherwise show up to 2 decimals, stripping trailing zeros
        return f'{fval:.2f}'.rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return str(value)
