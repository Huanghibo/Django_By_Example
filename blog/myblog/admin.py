from django.contrib import admin
from .models import User, Post, Category, Tag, Comment

admin.site.site_header = '管理系统'
admin.site.site_title = '管理系统'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 设置想在后台列表页面显示的模型字段
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    # 设置后台可以进行筛选的字段
    list_filter = ('status', 'created_time', 'author')
    # 设置后台可以搜索的字段
    search_fields = ('title', 'body')
    # prepopulated预填充，表示通过title来填充slug字段
    prepopulated_fields = {'slug': ('title',)}
    # 显示外键的详细信息，不再使用下拉框（只适用于外键）
    raw_id_fields = ('author',)
    # 搜索框的下方，可以通过日期层次快速导航的栏
    date_hierarchy = 'created_time'
    # 文章排序规则
    ordering = ['status', 'created_time']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'url', 'text', 'created_time')
    search_fields = ('name', 'email', 'text')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'email', 'confirmed', 'last_login', 'is_active',  'is_staff', 'is_superuser', 'date_joined', 'sex')
    list_filter = ('confirmed', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')


@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ('name', 'created_time')
    search_fields = ('name',)


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name', 'created_time')
    search_fields = ('name',)
