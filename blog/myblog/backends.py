from .models import User


class EmailBackend(object):
    """ 使用email进行认证 """
    def authenticate(self, request, **credentials):
        # 注意登录表单中用户输入的用户名或者邮箱的 field 名均为 username
        # 尝试从参数中获取emaik，如果没有就默认获取username
        email = credentials.get('email', credentials.get('username'))
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            if user.check_password(credentials["password"]):
                return user

    def get_user(self, user_id):
        """ 该方法是自定义认证后台必须的，可以直接拷贝 """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
