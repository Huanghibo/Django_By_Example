from django.urls import include, path
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done, \
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from . import views

app_name = 'account'
urlpatterns = [
    # 注册
    path('register/', views.register, name='register'),
    # 登录
    # path('login/', views.user_login, name='login'),
    path('login/', login, {'template_name': 'account/login.html'}, name='login'),
    # 退出
    path('logout/', logout, {'template_name': 'account/logged_out.html'}, name='logout'),
    # 退出然后重定向到登录页面， logtou_then_login 视图不需要任何模板，因为它执行的是重定向到登录的视图
    path('logout_then_login/', logout_then_login, name='logout_then_login'),
    # 控制面板
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    # 编辑用户资料
    path('edit/', views.edit, name='edit'),
    # 用户中心
    path('users/', views.user_list, name='user_list'),
    # 关注
    # 因为follow包含在下面的路由<username>匹配规则中，所以本路由必须放在<username>匹配规则之前
    # 每次HTTP请求，Django都会对所有存在的URL模式进行匹配直到第一条匹配成功才会停止匹配
    path('users/follow/', views.user_follow, name='user_follow'),
    # 用户详细信息
    path('users/<username>/', views.user_detail, name='user_detail'),
]
