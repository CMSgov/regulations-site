from django.template import Library, loader

register = Library()


@register.simple_tag()
def render_nested(*templates, context=None, **kwargs):
    return loader.select_template(templates).render(context or kwargs)
