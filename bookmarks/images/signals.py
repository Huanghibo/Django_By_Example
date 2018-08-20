from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image


# 小心使用信号，因为它们会给理解控制流制造困难，在很多场景下如果知道通知哪个receiver就可以避免使用信号
# 在使用非规范化字段之前应该考虑其他几种提高性能的方法：数据库索引、最佳化查询以及缓存
# receiver()装饰器将users_like_changed函数注册成receiver函数，然后将该函数附加给m2m_changed信号，将users_like_changed函数与Image.users_like.through连接
# 这样users_like_changed函数只有当m2m_changed信号被Image.users_like.through执行的时候才被调用
# 还有个方式是注册receiver函数，由使用Signal对象的connect()方法组成，Django信号是同步阻塞的，使用异步任务将导致信号混乱，但是当你的代码只接受一个信号的通知时可以联合两者来执行异步任务
# 当连接的信号发送的时候，必须连接receiver函数并提供信号，这样它才会被调用。有个用来注册信号的推荐方法是在应用配置类中把它们导入到ready()方法中，Django提供应用注册允许对应用进行配置和内省。
# 为了注册信号receiver函数，当使用receiver()装饰器的时候，只需要在应用的AppConfig类中的ready()方法中导入信号模块，ready()方法在应用注册被完整填充的时候就调用，它可以包含应用的其他初始化内容
@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.users_like.count()
    instance.save()
