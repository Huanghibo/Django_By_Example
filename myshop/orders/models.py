from django.db import models
from shop.models import Product
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupons.models import Coupon


class Order(models.Model):
    first_name = models.CharField('姓', max_length=50)
    last_name = models.CharField('名', max_length=50)
    email = models.EmailField('邮箱')
    address = models.CharField('地址', max_length=250)
    postal_code = models.CharField('邮编', max_length=20)
    city = models.CharField('城市', max_length=100)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    paid = models.BooleanField('已支付', default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='orders', null=True, blank=True, verbose_name='优惠码')
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='折扣')

    class Meta:
        ordering = ('-created',)
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def __str__(self):
        return '订单号{}'.format(self.id)

    # 折扣后的总价
    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * (self.discount / Decimal('100'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单号')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='产品')
    price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('数量', default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
