from django.apps import AppConfig


class PaymentConfig(AppConfig):
    # name参数是应用名字
    name = 'payment'
    verbose_name = 'Payment'

    # 在ready()方法中导入信号，确保应用初始化时apps被加载
    def ready(self):
        # 导入信号处理器
        import payment.signals
