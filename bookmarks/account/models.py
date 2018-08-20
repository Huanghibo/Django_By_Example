from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model):
    # 如果没在settings中自定义AUTH_USER_MODEL常量，则AUTH_USER_MODEL默认为Django自带的User
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    date_of_birth = models.DateField('生日', default='1900-01-01', null=True)
    # 图片上传字段，需要指定upload_to目录
    photo = models.ImageField('头像', upload_to='users/%Y/%m/%d', default='images/photo.jpg')

    def __str__(self):
        return '用户{}的详细信息'.format(self.user.username)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name


# 使用默认的User模型并且不想修改它，而且需要存储关系建立的时间
# 给多对多关系使用中间模型后，add()，create()以及remove()等关系管理器方法将不可用，需要使用创建或删除中间模型的实例的方法
class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE, verbose_name='关注')
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE, verbose_name='被关注')
    created = models.DateTimeField('关注时间', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '关注系统'
        verbose_name_plural = verbose_name
        ordering = ('-created',)

    def __str__(self):
        return '{}关注了{}'.format(self.user_from, self.user_to)


# 不推荐使用add_to_class()为模型添加字段，在大部分场景中，在Profile模型添加字段是更好的方法
User.add_to_class('following',
                  models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False))
