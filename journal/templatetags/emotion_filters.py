from django import template

register = template.Library()

@register.filter
def to_percentage(value):
    """
    Convert decimal (0.0-1.0) to percentage (0-100)
    """
    try:
        return int(float(value) * 100)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """
    Multiply value by arg
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sentiment_to_position(value):
    """
    Convert sentiment (-1 to 1) to position (0 to 100)
    """
    try:
        # Convert -1,1 range to 0,100 range
        position = ((float(value) + 1) / 2) * 100
        return int(position)
    except (ValueError, TypeError):
        return 50  # neutral position