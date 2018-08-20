from django import template

register = template.Library()


@register.filter
def model_name(obj):
    try:
        # 获取模型名
        return obj._meta.model_name
    except AttributeError:
        return None
