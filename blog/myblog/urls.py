from django.urls import include, path
# from django.contrib.auth.views import login
from . import views

app_name = 'blog'
urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    # 文章ID风格的文章地址
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
    # 个人中心
    path('accounts/profile/', views.user_index, name='usersindex'),
    path('user/index/', views.user_index, name='user_index'),
    path('user/', views.user_index, name='user_index'),
    # 注销
    path('user/logout/', views.logout_view, name='logout'),
]