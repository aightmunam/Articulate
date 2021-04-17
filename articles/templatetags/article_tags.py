"""
Template tags for articles app
"""
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    """
    Converts text into markdown format
    """
    return mark_safe(markdown.markdown(text))
