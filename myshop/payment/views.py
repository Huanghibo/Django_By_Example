from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from paypal.standard.forms import PayPalPaymentsForm
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt


def payment_process(request):
    # 从session中获取订单号
    order_id = request.session.get('order_id')
    # 通过订单号获取订单详情
    order = get_object_or_404(Order, id=order_id)
    # 当前访问的域名
    host = request.get_host()
    paypal_dict = {
        # PayPal商业账户
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        # 折扣后的总价，精度设置为0.01级别
        'amount': '%.2f' % order.get_total_cost().quantize(Decimal('.01')),
        # PayPal账单中的商品名
        'item_name': '订单号{}'.format(order.id),
        # PayPal账单名
        'invoice': str(order.id),
        # 货币代码，和在PayPal账户中设置的货币一致
        'currency_code': 'USD',
        # Paypal会发送IPN到支付通知URL，使用django-paypal提供的paypal-ipn的URL
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        # 支付成功后返回页面
        'return_url': 'http://{}{}'.format(host, reverse('payment:done')),
        # 取消支付后返回页面
        'cancel_return': 'http://{}{}'.format(host, reverse('payment:canceled')),
    }
    # PayPalpaymentsForm 将会被渲染成用户只能看到Buy now按钮的带有隐藏字段的标准表单，用户点击该按钮时，表单将会通过POST方法提交到PayPal
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment/process.html', {'order': order, 'form': form})


# 使用csrf_exempt装饰器取消csrf token验证，因为PayPal通过POST方法将用户重定向到下面两个视图
@csrf_exempt
def payment_done(request):
    return render(request, 'payment/done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html')