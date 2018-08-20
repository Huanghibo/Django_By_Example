from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
import weasyprint
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .task import order_created
from shop.models import Product
from shop.recommender import Recommender


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # 如果session中有优惠码，就修改order模型中的优惠码、折扣字段再保存
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            r = Recommender()
            r.products_bought([item['product'] for item in cart])
            # 这里还是按原价算
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
                # 清空购物车
                cart.clear()
                # 执行发送邮件通知的异步任务，任务将会被添加进队列中，将会尽快被worker执行
                order_created.delay(order.id)
                # 在session中保存订单号
                request.session['order_id'] = order.id
                # 重定向到支付网关
                return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


# 要求访问的用户is_active以及is_staff都是True
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # 变量order传入模板并渲染，保存到变量html
    html = render_to_string('orders/order/pdf.html', {'order': order})
    # 表示响应的是pdf文件
    response = HttpResponse(content_type='application/pdf')
    # 表示响应携带附件
    response['Content-Disposition'] = 'filename="订单_{}.pdf"'.format(order.id)
    # 根据html代码和CSS生成PDF
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    # write_pdf生成的response是PDF文件
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response
