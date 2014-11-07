from django import template
from datetime import datetime
register = template.Library()

@register.filter
def pretty_date(datetime):
    return datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")
