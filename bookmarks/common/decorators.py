from django.http import HttpResponseBadRequest


# 大多数JS库发起的AJAX请求都包含HTTP_X_REQUESTED_WITH HTTP头，其中包含XMLHttpRequest值
# Django Request对象提供is_ajax()方法，会检查请求是否带有XMLHttpRequest值（是否是AJAX 请求）
# 装饰器目标是限制AJAX视图只接收由AJAX发起的请求，当请求不是AJAX时返回HttpResponseBadRequest（HTTP 400）对象
def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
