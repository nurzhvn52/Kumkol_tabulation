from django import template

register = template.Library()

@register.filter
def get_fact(queryset, employee_id):
    return queryset.filter(employee_id=employee_id)

@register.filter
def get_fact_for_day(queryset, day):
    return queryset.filter(date=day).first()
