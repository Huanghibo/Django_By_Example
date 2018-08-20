from rest_framework.permissions import BasePermission


# 定制权限
class IsEnrolled(BasePermission):
    # 检查执行请求的用户是否存在Course对象的students中
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()