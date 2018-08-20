from django.db import models
from django.conf import settings
from django.urls import reverse
# from django.utils.text import slugify
from uuslug import slugify


class Image(models.Model):
    # 一个用户可以post多张图片，但每张图片只能由一个用户上传，related_name是关联对象反向引用的名字
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images_created', verbose_name='用户')
    title = models.CharField('标题', max_length=200)
    # 只包含字母、数字、下划线、和连字符的标签，用于创建优美的SEO的URL
    slug = models.SlugField('SLUG', max_length=200, blank=True)
    url = models.URLField('网址')
    # ImageField类型必须设置upload_to参数
    image = models.ImageField('图片', upload_to='images/%Y/%m/%d')
    description = models.TextField('描述', blank=True)
    # 因为将要很频繁地使用filter()，exclude(),order_by()查询，所以在数据库中为这个字段创建索引，索引会改善查询的执行效率
    # 也可以使用 Meta.index_together 为多个字段创建索引
    created = models.DateField('上传时间', auto_now_add=True, db_index=True)
    # 一个用户可能喜欢很多张图片，一张图片也可能被很多用户喜欢
    # 定义ManyToMany字段时，Django会用两张表的主键创建中间联接表，ManyToMany字段可以在任意两个相关联的表中创建
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_liked', blank=True, verbose_name='喜欢的人')
    total_likes = models.PositiveIntegerField('有多少人喜欢', db_index=True, default=0)

    def __str__(self):
        return self.title

    # 设置绝对地址获取方法
    def get_absolute_url(self):
        # 使用reverse转向到视图的命名空间
        return reverse('images:detail', args=(self.id, self.slug))

    # 重写save()方法，自动生成slug字段
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            super(Image, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '图片分享'
        verbose_name_plural = verbose_name
        ordering = ['-created']
