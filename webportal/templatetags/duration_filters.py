from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def to_minutes(duration):
    """Convert a timedelta duration to minutes"""
    if duration is None:
        return 0
    if isinstance(duration, timedelta):
        return int(duration.total_seconds() / 60)
    return 0
