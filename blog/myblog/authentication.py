from .models import User


# Django使用认证后台的authenticate()方法来认证用户之后通过get_user()方法取回 User 对象放置到持续的用户会话中
class EmailAuthBackend(object):
    """ 使用email进行认证 """
    # authenticate()方法将用户信息当成参数，如果用户成功的认证就返回 True，否则返回 False
    def authenticate(self, username=None, password=None):
        try:
            # 根据email获取用户
            user = User.objects.get(email=username)
            # check_password()方法检查密码，会对提供的密码进行哈希化来和数据库中存储的加密密码进行匹配
            if user.check_password(password):
                return user
            # 其他情况默认密码不通过，返回None
            return None
        # 未找到用户
        except User.DoesNotExist:
            return None

    # get_user()方法将用户的ID当成参数然后返回用户对象
    def get_user(self, user_id):
        """  该方法是自定义认证后台必须的，可以直接拷贝 """
        try:
            # 根据user_id获取用户
            return User.objects.get(pk=user_id)
        # 未找到用户
        except User.DoesNotExist:
            return None
