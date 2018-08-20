from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # changefreq和priority既可以是方法也可以是属性
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        # items()方法返回sitemap中所包含对象的查询集，默认在每个对象中调用get_absolute_url()方法来获取它的URL
        # 如果需要为每个对象指定URL，可以重写location方法
        return Post.published.all()

    def lastmod(self, obj):
        # lastmod方法接收items()返回的每个对象并且返回对象的最后修改时间
        return obj.modified_time
