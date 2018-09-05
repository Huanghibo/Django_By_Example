from .forms import SearchForm


# 上下文处理器是函数，接收request对象作为参数，返回对象字典，这些对象可用于所有使用RequestContext渲染的模板
def searchform(request):
    form = SearchForm()
    return {'form': form}
