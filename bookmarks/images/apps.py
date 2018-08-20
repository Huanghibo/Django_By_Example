from django.apps import AppConfig


class ImagesConfig(AppConfig):
    # name参数是应用名字
    name = 'images'
    verbose_name = '图片收藏'

    def ready(self):
        # import signal handlers
        import images.signals