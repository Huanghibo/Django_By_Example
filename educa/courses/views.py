from braces.views import LoginRequiredMixin, PermissionRequiredMixin, CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.apps import apps
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.cache import cache
# Django 配备有几个缓存后端，他们是：
# backends.memcached.MemcachedCache或backends.memcached.PyLibMCCache：内存缓存后端，内存缓存是快速、高效的基于内存的缓存服务器。后端的使用取决于选择的Python绑定
# backends.db.DatabaseCache： 数据库作为缓存系统
# backends.filebased.FileBasedCache：文件储存系统，把每个缓存值序列化和储存为单一的文件
# backends.locmem.LocMemCache：本地内存缓存后端，默认缓存后端
# backends.dummy.DummyCache：用于开发的虚拟缓存后端，它实现了缓存交互界面而不用真正的缓存任何东西，此缓存是独立进程且是线程安全的
from .forms import ModuleFormSet
from .models import Course, Module, Content, Subject
from students.forms import CourseEnrollForm


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        # 当前用户必须是查询集的作者
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        # 当前用户必须是表单实例的作者
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


# 登录限制，并指定模型为Course，当前用户必须是查询集的作者
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course


# 指定模型为Course、查询集限制、表单限制
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    # 指定字段构建模型
    fields = ['subject', 'title', 'slug', 'overview']
    # 表单提交成功后的重定向地址
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'


# 指定模型为Course、查询集限制
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'


# 指定模型为Course、查询集限制、表单限制、权限限制，继承自OwnerCourseEditMixin也会继承他的模板form.html
class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    # 权限要求
    permission_required = 'courses.add_course'


# PermissionRequiredMixin会在用户使用视图时检查该用户是否具有permission_required属性中设置的权限
# 指定模型为Course、查询集限制、表单限制、权限限制，继承自OwnerCourseEditMixin也会继承他的模板form.html
class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    # 权限要求
    permission_required = 'courses.change_course'


# 指定模型为Course、查询集限制、表单限制、权限限制
class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/delete.html'
    # 权限要求
    permission_required = 'courses.delete_course'


# 指定模型为Course、查询集限制、表单限制、权限限制
# TemplateResponseMixin负责渲染模板以及返回HTTP响应，并提供render_to_ response()方法来传递上下文并渲染模板
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    # 避免重复构建formset代码，使用可选数据为给定的Course对象创建ModuleFormSet对象
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    # 判断被给定的模型名是否是text，video，image，file四种内容模型中的一种，之后使用apps模块通过给定的模型名获取实际的类，如果给予的模型名不是其中的一种，则返回None
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    # 使用modelform_factory()函数构建动态表单，由于只给Text，Video，Image，File模型构建表单，所以使用exclude参数指定要从表单中排除的公共字段，并允许自动包含所有其他属性
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    # 当收到GET请求的时候会被执行
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    # 收到POST请求的时候会执行,传递所有提交的数据和文件给该表单构建模型表单,之后验证该表单,如果验证通过，创建新的对象并且在保存该对象到数据库之前分配request.user作为该对象的拥有者
    # 如果没有提供id，当前用户将创建新的对象而不是更新已经存在的对象，如果是新的对象，将创建Content对象给给定的模块并且关联新的内容到该模块
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # 没有id的话就创建新内容
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        # 删除关联的Text，Video，Image，File对象
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


# 继承自CsrfExemptMixin避免在POST请求中检查CSRF token，继承自JsonRequestResponseMixin将请求的数据分析为JSON并且将响应也序列化成JSON并且返回pplication/json内容类型的HTTP响应
class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        # 主题没有缓存的话就查询并写入缓存
        if not subjects:
            # 通过聚合获取主题总数、课程总数
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        # 如果提供有主题SLUG，获取主题和课程
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = 'subject_{}_courses'.format(subject.id)
            # 从缓存中根据主题ID读取，如果不存在缓存中就查询并写入缓存
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        # 如果没有传递slug参数，就试图从缓存中读取所有课程，如果缓存中不存在，就查询出all_courses并缓存
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects, 'subject': subject, 'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        # 初始化带有当前Course对象的表单的隐藏course字段
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context
