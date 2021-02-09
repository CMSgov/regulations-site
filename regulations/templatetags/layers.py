from django import template
from regulations.generator import api_reader

register = template.Library()

@register.filter(name='internalcitation')
def internalcitation(value, arg):
    label = "-".join(arg)
    client = api_reader.ApiReader()
    result = client.layer("internal-citations", "cfr", label, "2016-27844")
    if result is None:
        return value
    try:
        citations = result[label]
        for citation in citations:
            original = value[citation["offsets"][0][0]:citation["offsets"][0][1]]
            value = value[:citation["offsets"][0][0]] + "-".join(citation["citation"]) + value[citation["offsets"][0][1]:]
        return value
    except KeyError:
        return value