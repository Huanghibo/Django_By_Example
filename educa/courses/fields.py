from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):

    # for_fields参数允许根据指定的字段进行计算并排序
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    # 重写pre_save方法
    def pre_save(self, model_instance, add):
        # 如果模型实力中没有attname的值
        if getattr(model_instance, self.attname) is None:
            try:
                # self.model检索该字段所属的模型类
                qs = self.model.objects.all()
                if self.for_fields:
                    # 通过模型字段中定义在for_fields参数中的字段的值来筛选查询集
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)
                # 得到最新实例的顺序，再+1得到值
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
                # 如果实例不存在，使用setattr()方法给在模型实例中的字段分配值并且返回值
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)
