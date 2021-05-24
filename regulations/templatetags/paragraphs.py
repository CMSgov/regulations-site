from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.filter(name='pdepth')
def internalcitation(value):
    return len(value.get("label", []) or []) - len(value.get("marker", []) or [])
