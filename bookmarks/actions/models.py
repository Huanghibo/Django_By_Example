from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    user = models.ForeignKey(User, related_name='actions', db_index=True, on_delete=models.CASCADE, verbose_name='用户')
    verb = models.CharField('动态', max_length=255)
    # 在target-ct字段使用limit_choices_to属性，把特定值的集合提供给他可以限制ForeignKey字段的内容，也就是限制模型集合（限制内容类型）
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE, related_name='target_obj', verbose_name='内容模型')
    target_id = models.PositiveIntegerField('被关联对象的主键', null=True, blank=True, db_index=True)
    # 定义和管理通用关系，使用通用关系替代外键可以让应用更加灵活
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField('操作时间', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '最新动态'
        verbose_name_plural = verbose_name
        ordering = ('-created',)
