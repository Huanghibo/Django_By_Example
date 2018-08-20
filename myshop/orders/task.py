from celery import task
from django.core.mail import send_mail
from .models import Order


# CELERY_ALWAYS_EAGER设置允许在本地用异步的方式执行任务而不是把他们发送向队列中，在不运行Celery、运行单元测试或者是运行在本地环境中的项目的情况下很有用
# 异步任务不仅仅适用于耗时进程，也适用于失败进程组中的进程
# Celery异步任务只是用task装饰的Python函数，推荐做法是只传递ID给任务函数然后在任务被执行的时候查找相关的对象
@task
def order_created(order_id):
    """ 通知用户已经下单 """
    order = Order.objects.get(id=order_id)
    subject = '成功下单！订单号{}'.format(order.id)
    message = '亲爱的用户{}\n\n你已经成功下单，订单号 {}。\n你的收件箱 {}，收件地址：{}\n邮编{},城市{},订单创建时间{}'.\
        format(order.last_name+order.first_name, order.id, order.email, order.address, order.postal_code, order.city, order.created)
    mail_sent = send_mail(subject, message, 'dstwhk@126.com', [order.email])
    return mail_sent
