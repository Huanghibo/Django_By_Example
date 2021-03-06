from django.urls import include, path
from django.contrib.auth.views import login, password_change, password_change_done, password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete
from django.contrib.sitemaps.views import sitemap
from . import views
from .feeds import AllPostsRssFeed
from .sitemaps import PostSitemap


sitemaps = {
    'posts': PostSitemap,
}


urlpatterns = [
    path('', views.index, name='index'),
    path('page/<int:page>', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    # ID风格的文章地址
    path('post/<int:pk>/', views.detail, name='detail'),
    # slug风格的文章地址
    path('<int:year>/<int:month>/<int:day>/<slug>/', views.detail_slug, name='detail_slug'),
    # path('<int:year>/<int:month>/<int:day>/<slug>/', views.archives, name='archives'),
    # 按年月归档
    path('archives/<int:year>/<int:month>/', views.ArchivesView.as_view(), name='archives'),
    # path('archives/<int:year>/<int:month>/', views.category, name='category'),
    # 分类
    path('category/<pk>/', views.CategoryView.as_view(), name='category'),
    # 搜索
    path('search/', views.search, name='search'),
    path('search/<q>/page/<int:page>', views.search_result, name='search_result'),
    # 跳转地址
    path('url/<shortcode>/', views.redirect_url, name='redirect_url'),
    # 标签
    path('tag/<pk>/', views.TagView.as_view(), name='tag'),
    # 联系我
    path('contact/', views.contact, name='contact'),

    # 注册
    path('user/register/', views.register, name='register'),
    # 登录
    # path('user/login/', login, {'template_name': 'users/login.html'}, name='login'),
    path('user/login/', views.login_view, name='login'),
    # 验证账户
    path('user/user_confirm', views.user_confirm, name='user_confirm'),
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
    path('user/password_reset/<uidb64>/<token>/', password_reset_confirm,
         {'template_name': 'users/password_reset_confirm.html'},
         name='password_reset_confirm'),
    # 密码重置成功
    path('user/password_reset_complete/', password_reset_complete,
         {'template_name': 'users/password_reset_complete.html'},
         name='password_reset_complete'),
    # 个人中心
    path('accounts/profile/', views.user_index, name='usersindex'),
    path('user/index/', views.user_index, name='user_index'),
    path('user/', views.user_index, name='user_index'),
    # 注销
    path('user/logout/', views.logout_view, name='logout'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('rss', AllPostsRssFeed(), name='rss'),
]
