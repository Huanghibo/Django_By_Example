import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


# 使用简单方式创建新动态并且避免保存大部分重复动态的快捷函数
def create_action(user, verb, target=None):
    # timezone.now()获取当前时间，方法同datetime.datetime.now()相同，但是返回的是timezone-aware对象，settings.py里面的USE_TZ用来启用或关闭时区的支持
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    # 检查最近1分钟的相似动态
    similar_actions = Action.objects.filter(user_id=user.id, verb=verb, created__gte=last_minute)
    if target:
        # 根据模型获取内容类型
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct, target_id=target.id)
    # 如果最近1分钟没有相似动态，创建新的动态
    if not similar_actions:
        action = Action(user=user, verb=verb, target=target)
        action.save()
        # 如果Action对象被创建返回True，否则返回False
        return True
    return False
