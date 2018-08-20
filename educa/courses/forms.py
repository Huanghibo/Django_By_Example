from django.forms.models import inlineformset_factory
from .models import Course, Module

# 在同一个页面中使用多个表单，这些表单组合为formsets，formsets能管理多个Form或者ModelForm表单实例
# 所有表单都可以一次性提交并且formset能实现一些额外的事，比如表单初始化数据展示、限制表单能够提交的最大数字、所有表单的验证
# formset有个is_valid()方法一次性验证所有表单，还可以提供初始数据给表单以及指定展示任意多的额外空表单
# inlineformset_factory给关联到Course对象Module对象动态的构建模型formset，extra设置在formset中显示的额外空表单数
# can_delete如果为True，Django将使所有表单包含布尔字段，该布尔字段将会渲染成复选框，允许删除该对象
ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description'], extra=2, can_delete=True)
