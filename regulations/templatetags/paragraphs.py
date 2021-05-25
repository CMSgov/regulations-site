from django import template

register = template.Library()


@register.filter(name='pdepth')
def internalcitation(value):
    depth = len(value.get("label", []) or []) - 2 
    if len(value.get("marker", []) or []) > 1:
        depth = depth - len(value.get("marker", []) or [])
    return depth
