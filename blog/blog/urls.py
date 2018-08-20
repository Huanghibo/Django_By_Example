"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth.views import login, password_change, password_change_done, password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete
from myblog.feeds import AllPostsRssFeed
from myblog.sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    # 默认后台
    path('admin/', admin.site.urls),
    # 文章富文本编辑器
    path('ueditor/', include('DjangoUeditor.urls')),
    # 验证码
    path('captcha', include('captcha.urls')),
    # blog首页
    path('', include('myblog.urls', namespace='blog')),
    # sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # RSS
    path('rss', AllPostsRssFeed(), name='rss'),
    # 修改密码
    path('user/password_change/', password_change, {'template_name': 'users/password_change_form.html'},
         name='password_change'),
    # 密码修改完成
    path('user/password_change_done/', password_change_done, {'template_name': 'users/password_change_done.html'},
         name='password_change_done'),
    # 通过邮箱重置密码
    path('user/password_reset/', password_reset, {'template_name': 'users/password_reset_form.html'},
         name='password_reset'),
    # 重置密码链接已发送
    path('user/password_reset_done/', password_reset_done, {'template_name': 'users/password_reset_done.html'},
         name='password_reset_done'),
    # 设置新密码
    path('user/password_reset/<uidb64>/<token>/', password_reset_confirm, {'template_name': 'users/password_reset_confirm.html'},
         name='password_reset_confirm'),
    # 密码重置成功
    path('user/password_reset_complete/', password_reset_complete, {'template_name': 'users/password_reset_complete.html'},
         name='password_reset_complete'),
]

# 在debug模式时通过static()函数改变对多媒体文件的服务。static()函数应该在开发环境中使用而不是生产环境。
# 绝对不要在生产环境中使用Django来服务静态文件！
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
