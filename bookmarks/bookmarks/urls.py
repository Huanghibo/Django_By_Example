from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done, \
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete

urlpatterns = [
    path('admin/', admin.site.urls),
    # 用户中心
    path('account/', include('account.urls', namespace='account')),
    # 图片分享
    path('images/', include('images.urls', namespace='images')),
    # 验证码
    path('captcha', include('captcha.urls')),
    # 社交网站认证
    path('', include('social_django.urls', namespace='social')),
    # 修改密码
    path('password_change/', password_change, {'template_name': 'account/password_change_form.html'},
         name='password_change'),
    # 密码修改完成
    path('password_change_done/', password_change_done, {'template_name': 'account/password_change_done.html'},
         name='password_change_done'),
    # 通过邮箱重置密码
    path('password_reset/', password_reset, {'template_name': 'account/password_reset_form.html'},
         name='password_reset'),
    # 重置密码链接已发送
    path('password_reset_done/', password_reset_done, {'template_name': 'account/password_reset_done.html'},
         name='password_reset_done'),
    # 设置新密码
    path('password_reset/<uidb64>/<token>/', password_reset_confirm,
         {'template_name': 'account/password_reset_confirm.html'},
         name='password_reset_confirm'),
    # 密码重置成功
    path('password_reset_complete/', password_reset_complete,
         {'template_name': 'account/password_reset_complete.html'}, name='password_reset_complete'),

]

# 在debug模式时通过static()函数改变对多媒体文件的服务。static()函数应该在开发环境中使用而不是生产环境。
# 绝对不要在生产环境中使用Django来服务静态文件！
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
