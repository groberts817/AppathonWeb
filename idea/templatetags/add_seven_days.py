from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name='add_seven_days')
def add_seven_days(value):
    newVal = value + timedelta(days=7)
    return newVal