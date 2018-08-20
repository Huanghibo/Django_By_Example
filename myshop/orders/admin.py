import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from .models import Order, OrderItem
from django.urls import reverse
from django.utils.safestring import mark_safe


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    # 表示响应为CSV文件
    response = HttpResponse(content_type='text/csv')
    # 表示响应包含附件
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    # 使用模型的_meta选项的get_fields()方法动态获取model字段，并排除多对多、一对多关系
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # 把字段名写入第一行
    writer.writerow([field.verbose_name for field in fields])
    # 写入数据
    for obj in queryset:
        data_row = []
        for field in fields:
            # 获取obj的field.name属性
            value = getattr(obj, field.name)
            # 如果value是时间格式化，则转换为字符串，因为CSV只接受字符串
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


# 设置函数在后台的显示名
export_to_csv.short_description = '导出为CSV'


def order_detail(obj):
    return mark_safe('<a href="{}">查看</a>'.format(reverse('orders:admin_order_detail', args=[obj.id])))


# allow_tags=True避免转义html标签
order_detail.allow_tags = True
order_detail.short_description = '订单详情'


def order_pdf(obj):
    return mark_safe('<a href="{}">PDF</a>'.format(reverse('orders:admin_order_pdf', args=[obj.id])))


order_pdf.allow_tags = True
order_pdf.short_description = 'PDF账单'


# TabularInline水平布局，StackedInline垂直布局
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', 'created', 'updated', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    # 内联元素允许在OrderAdmin的同一页引用OrderItem模型，并且将其作为父模型
    inlines = [OrderItemInline]
    # 添加actions，也就是管理操作
    actions = [export_to_csv]


admin.site.register(Order, OrderAdmin)
