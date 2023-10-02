from django import template

register = template.Library()


@register.filter
def add(value, arg):
    return int(value) + int(arg)


@register.filter
def subtract(value, arg):
    return int(value) - int(arg)
