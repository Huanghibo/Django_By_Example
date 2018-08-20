from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('分类', max_length=200, db_index=True)
    slug = models.SlugField('分类别名', max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='分类')
    name = models.CharField('名称', max_length=200, db_index=True)
    slug = models.SlugField('产品别名', max_length=200, db_index=True)
    image = models.ImageField('图片', upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField('描述', blank=True)
    # 十进制字段，使用DecimalField而不是FloatField来避免精度问题，设置最长为10位数字，包括2位小数
    # 货币值总是使用DecimalField字段，DecimalField使用的是Python中的Decimal类型，FloatField使用Python的float类型
    price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    # 正整数字段
    stock = models.PositiveIntegerField('库存')
    available = models.BooleanField('有效', default=True)
    created = models.DateTimeField('发布时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ('name',)
        # index_together元选项指定id和slug字段的共同索引
        index_together = (('id', 'slug'),)
        verbose_name = '产品'
        verbose_name_plural = '产品'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
