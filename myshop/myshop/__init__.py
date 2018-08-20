# 导入celery 确保在Django启动时就加载celery
from .celery import app as celery_app