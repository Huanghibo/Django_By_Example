from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.CourseListView.as_view(), name='course_list'),
    path('accounts/login/', auth_views.login, name='login'),
    path('accounts/logout/', auth_views.logout, name='logout'),
    path('course/mine/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('course/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('course/<int:pk>/module/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    path('course/module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(), name='module_content_create'),
    path('course/module/<int:module_id>/content/<model_name>/<int:id>/', views.ContentCreateUpdateView.as_view(), name='module_content_update'),
    path('course/content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),
    path('course/module/<module_id>/', views.ModuleContentListView.as_view(), name='module_content_list'),
    path('course/module/order/', views.ModuleOrderView.as_view(), name='module_order'),
    path('course/content/order/', views.ContentOrderView.as_view(), name='content_order'),
    path('course/subject/<subject>/', views.CourseListView.as_view(), name='course_list_subject'),
    path('course/<slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('students/', include('students.urls')),
    path('api/', include('courses.api.urls', namespace='api')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)