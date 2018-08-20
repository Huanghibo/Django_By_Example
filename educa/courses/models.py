from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .fields import OrderField


class Subject(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = '主题'
        verbose_name_plural = verbose_name
        ordering = ('title',)

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_created', verbose_name='教师')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses', verbose_name='主题')
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField(verbose_name='概述')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True, verbose_name='学生')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ('-created',)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='课程')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    # 根据课程指定字段的顺序
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

    class Meta:
        ordering = ['order']
        verbose_name = '课程模块'
        verbose_name_plural = verbose_name


class Content(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents', verbose_name='模块')
    # limit_choices_to参数限制可以被通用关系使用的ContentType对象，model__in字段通过model属性给ContentType对象(就像'text','video','image',或者'file')查找过滤查询
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('text', 'video', 'image', 'file')}, verbose_name='内容模型')
    object_id = models.PositiveIntegerField(verbose_name='实例ID')
    # 通过结合前两个字段，GenericForeignKey字段指向被关联的对象，item字段允许检索或者直接设置关联对象，它的功能是建立在其他两个字段之上
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = '内容'
        verbose_name_plural = verbose_name


class ItemBase(models.Model):
    # owner字段被定义在抽象类中，所以给每个子模型设置不同的related_name，在related_name给model类名指定占位符，类似 %(class)s
    # 每个子模型都会自动生成名称为text_related,file_related,image_related,vide0_related的related_name
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_related', verbose_name='作者')
    title = models.CharField(max_length=250, verbose_name='标题')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # abstract = True表示这是个抽象模型，里面的字段不会写入数据库的表，继承于这个模型的模型才会写入数据库的表
    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('courses/content/{}.html'.format(self._meta.model_name), {'item': self})


class Text(ItemBase):
    content = models.TextField(verbose_name='内容')

    class Meta:
        verbose_name = '文本'
        verbose_name_plural = verbose_name


class File(ItemBase):
    file = models.FileField(upload_to='files', verbose_name='文件')

    class Meta:
        verbose_name = '文件'
        verbose_name_plural = verbose_name


class Image(ItemBase):
    file = models.FileField(upload_to='images', verbose_name='图片')

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = verbose_name


class Video(ItemBase):
    url = models.URLField(verbose_name='网址')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name
