from django import template
from datetime import datetime
register = template.Library()

@register.filter
def get_class_name(obj):
    return obj.__class__.__name__
