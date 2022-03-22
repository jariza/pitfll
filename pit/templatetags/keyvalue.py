from django import template

def keyvalue(d, k):
    if not isinstance(d, dict):
        return ''
    if k not in d:
        return ''
    return d[k]

register = template.Library()
register.filter('keyvalue', keyvalue)