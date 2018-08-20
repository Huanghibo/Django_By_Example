from django.shortcuts import get_object_or_404
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import weasyprint
from io import BytesIO


def payment_notification(sender, **kwargs):
    ipn_obj = sender
    print(ipn_obj.payment_status)
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # 支付成功
        order = get_object_or_404(Order, id=ipn_obj.invoice)
        # 修改paid字段值为True
        order.paid = True
        order.save()
        # 生成账单邮件
        subject = '账单号{} - 在线商店'.format(order.id)
        message = '这是你的最新支付信息，详情请查看附件。'
        email = EmailMessage(subject, message, 'dstwhk@126.com', [order.email])
        html = render_to_string('orders/order/pdf.html', {'order': order})
        out = BytesIO()
        stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
        # write_pdf生成的out是BytesIO字节流
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
        # 把PDF作为email的附件，getvalue()获取写入out的二进制内容，application/pdf指定文件类型
        email.attach('订单_{}.pdf'.format(order.id), out.getvalue(), 'application/pdf')
        # send e-mail
        email.send()


# 当获取自PayPal的IPN信息是正确的并且在数据库中不存在相同的IPN，valid_ipn_received信号会被触发
valid_ipn_received.connect(payment_notification)
