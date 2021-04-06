import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

el = ('<span class="search-highlight">', '</span>')


@register.filter(name='highlight')
@stringfilter
def highlight(text, arg):
    search_terms = arg.split()
    for term in search_terms:
        text = wrap(term, el, text)
    return mark_safe(text)


def wrap(term, el, text):
    re_term = re.compile(rf"{term}", re.IGNORECASE)
    result = set(re_term.findall(text))
    for match in result:
        wrapped = f'{el[0]}{match}{el[1]}'
        text = text.replace(match, wrapped)
    return text