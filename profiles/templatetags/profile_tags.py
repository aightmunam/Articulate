from django import template

register = template.Library()


@register.filter(name='relevant_css')
def insert_relevant_class(favorite):
    if favorite:
        return "btn-success \" disabled"
    return "btn-outline-success"
