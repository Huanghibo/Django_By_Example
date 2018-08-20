from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from ..models import Subject, Course
from .permissions import IsEnrolled


class SubjectListView(generics.ListAPIView):
    # 取回对象
    queryset = Subject.objects.all()
    # 序列化对象
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# 用来在课程中报名的URL现在已经是由路由动态的生成，URL保持不变，因为它使用操作名enroll动态的进行构建
# ReadOnlyModelViewSet提供只读的操作list()和retrieve()，前者用来排列对象，后者用来取回单独的对象
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # 指定这个类是在单独对象上被执行的操作，指定视图只允许POST方法，并且设置认证和权限类
    @action(detail=True, methods=['post'], authentication_classes=[BasicAuthentication], permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        # 获取Course对象
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    # 指定只允许GET方法访问，使用IsAuthenticated和定制的IsEnrolled权限，确保只有在课程中报名的用户才能访问课程的内容
    @action(detail=True, methods=['get'], serializer_class=CourseWithContentsSerializer, authentication_classes=[BasicAuthentication], permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
