import os
from celery import Celery
from django.conf import settings


# 为celery设置默认DJANGO_SETTINGS_MODULE 变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
app = Celery('myshop')
app.config_from_object('django.conf:settings')
# Celery自动查找INSTALLED_APPS设置中的应用，然后在每个应用路径下查找task.py来加载定义在其中的异步任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
