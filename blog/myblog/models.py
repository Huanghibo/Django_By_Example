from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
from DjangoUeditor.models import UEditorField
# from taggit.managers import TaggableManager
from uuslug import slugify


# 拓展User模型，增加性别字段
class User(AbstractUser):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    sex = models.CharField('性别', max_length=32, choices=gender, default="男")
    confirmed = models.BooleanField('已验证', default=False)

    # 这里pass即可
    class Meta(AbstractUser.Meta):
        pass


class Category(models.Model):
    name = models.CharField('分类', max_length=100)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Tag(models.Model):
    name = models.CharField('标签', unique=True, max_length=100)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class PublishedManager(models.Manager):
    # 重写get_queryset可以自定义查询集的返回结果
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    # 前面为数据库中的值，后面为显示在页面上的文字
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )
    title = models.CharField('标题', max_length=70)
    # 存储比较短的字符串可以使用 CharField，但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本。
    # unique_for_date是为了和下面的created_time保证同一个日期的slug值是唯一的
    # default是默认值，max_length为最大长度，blank=True表示可以为null
    slug = models.SlugField(max_length=250, unique_for_date='created_time', null=True)
    # imagePath:图片上传的路径,如"images/",实现上传到"{{MEDIA_ROOT}}/images"文件夹，filePath:附件上传的路径，如"files/",
    # 实现上传到"{{MEDIA_ROOT}}/files"文件夹。width，height:编辑器的宽度和高度，以像素为单位。
    # toolbars:配置你想显示的工具栏，取值为mini,normal,full,besttome, 代表小，一般，全部。
    body = UEditorField('正文', height=300, width=1000, default='', blank=True, imagePath="uploads/images/",
                        toolbars='besttome', filePath='uploads/files/')
    # 分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    # auto_now_add是在新增的时候自动添加当前时间，auto_now是在修改的时候自动添加当前时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    modified_time = models.DateTimeField('修改时间', auto_now=True)
    excerpt = models.CharField('摘要', max_length=200, blank=True)
    # verbose_name 外键在编辑文章界面展示的名字，on_delete=models.CASCADE 外键删除时被管理的表内的主键也强制删除
    category = models.ForeignKey(Category, verbose_name='所属分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    # tags = TaggableManager()
    author = models.ForeignKey(User, verbose_name='所属作者', on_delete=models.CASCADE)
    views = models.PositiveIntegerField('浏览量', default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    objects = models.Manager()  # 默认manager
    published = PublishedManager()  # 自定义manager

    # 自定义方法，方便views.py里面调用
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        # 如果没有生成slug
        if not self.slug:
            self.slug = slugify(self.title)
        # 如果没有填写摘要
        if not self.excerpt:
            # strip_tags 去掉HTML文本的全部HTML标签，从文本摘取前200个字符赋给excerpt
            self.excerpt = strip_tags(self.body)[:200]
        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    # 自定义方法，获取URL绝对地址
    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.pk])

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='所属文章')
    name = models.CharField('名字', max_length=100)
    # 邮件规则，比如@
    email = models.EmailField('邮箱', max_length=255)
    # URL规则，比如http://
    url = models.URLField('个人主页', blank=True)
    text = models.TextField('内容')
    created_time = models.DateTimeField('评论时间', auto_now_add=True)

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class ConfirmString(models.Model):
    code = models.CharField('确认码', max_length=256)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField('注册时间', auto_now_add=True)

    def __str__(self):
        return self.user.username + ":   " + self.code

    class Meta:
        verbose_name = "确认码"
        verbose_name_plural = verbose_name
        ordering = ["-created_time"]
