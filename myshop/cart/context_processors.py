# 上下文处理器是接收request对象为参数并返回已经添加请求上下文字典的Python函数，在需要让变量在所有模板都可用时很有用
# django.template.context_processors.debug ：在上下文中设置debug布尔值和sql_queries变量，来表示在request中执行的SQL查询语句表
# django.template.context_processors.request ：在上下文中设置request变量
# django.contrib.auth.context_processors.auth ：在请求中设置用户变量
# django.contrib.messages.context_processors.messages ：在包含所有使用消息框架发送的信息的上下文中设置messages变量
# django.template.context_processors.csrf：避免跨站请求攻击，这个上下文处理器不在设置中，但是它总是可用的并且由于安全原因不可被关闭。
from .cart import Cart


# 将当前购物车添加进模板请求上下文中，这样就可以在任意模板中获取任意购物车，上下文处理器是函数，接收request对象作为参数，返回对象字典，这些对象可用于所有使用RequestContext渲染的模板
def cart(request):
    # 使用request对象实例化购物车，作为在任何模板都可用的cart的参数，上下文处理器会在所有的使用RequestContext的请求中执行
    return {'cart': Cart(request)}
