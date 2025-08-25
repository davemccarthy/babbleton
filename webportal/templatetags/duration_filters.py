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

@register.filter
def format_duration(seconds):
    """Format seconds into a readable duration string (e.g., 5m 30s)"""
    if seconds is None:
        return '-'
    
    try:
        seconds = float(seconds)
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"
    except (ValueError, TypeError):
        return '-'

@register.filter
def is_external(value):
    """Check if a value represents an external session (handles various boolean formats)"""
    if value is None:
        return False
    
    # Handle string representations
    if isinstance(value, str):
        return value.lower() in ['true', 't', '1', 'yes', 'y']
    
    # Handle boolean values
    if isinstance(value, bool):
        return value
    
    # Handle numeric values
    if isinstance(value, (int, float)):
        return value == 1
    
    return False

@register.filter
def seconds_to_minutes(seconds):
    """Convert seconds to minutes for display"""
    if seconds is None or seconds <= 0:
        return 0
    
    try:
        return int(seconds / 60)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_acd(seconds):
    """Format ACD (Average Call Duration) from seconds to readable format"""
    if seconds is None or seconds <= 0:
        return '-'
    
    try:
        seconds = float(seconds)
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"
    except (ValueError, TypeError):
        return '-'
