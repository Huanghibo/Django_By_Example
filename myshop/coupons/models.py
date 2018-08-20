from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='优惠码')
    valid_from = models.DateTimeField(verbose_name='生效日期')
    valid_to = models.DateTimeField(verbose_name='过期日期')
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='折扣')
    active = models.BooleanField(verbose_name='有效')

    def __str__(self):
        return self.code

    class Meta:
        ordering = ('valid_from', 'valid_to')
        verbose_name = '优惠券'
        verbose_name_plural = '优惠券'
