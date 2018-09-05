import hashlib
import datetime
import threading
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models import FilteredRelation, Q, Count
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import User, Post, Category, Tag, Comment, ConfirmString
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from taggit.models import Tag
from .forms import CommentForm, RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.http import Http404


# 加密确认码
def hash_code(string, salt='myblog'):
    hash = hashlib.sha256()
    # 加点盐
    string += salt
    # update方法只接收bytes类型
    hash.update(string.encode())
    return hash.hexdigest()


# 生成确认码
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    ConfirmString.objects.create(code=code, user=user)
    return code


class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )


# 多线程发送邮件
def send_email(subject, text, email):
    send_mail = SendMail(subject, text, email)
    send_mail.start()


def contact(request):
    """用户中心首页"""
    return render(request, 'users/index.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # 验证数据的合法性，包括使用forms.py里的自定义方法
        if form.is_valid():
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            try:
                # authenticate()方法逐一调用认证后台的authenticate方法来验证用户提供登录凭据的合法性
                authenticated_user = authenticate(username=username, password=password1)
                # user = User.objects.get(username=username)
                # 如果用户名密码正确则登录
                login(request, authenticated_user)
                # 用户是未认证状态
                if not authenticated_user.confirmed:
                    # 查询用户的验证码，如果查询不到会报错RelatedObjectDoesNotExist
                    code = authenticated_user.confirmstring.code
                    # code = ConfirmString.objects.get(user_id=user.id).code
                    # 发送验证码邮件
                    subject = '来自我的博客的注册确认邮件'
                    text = '''
                                    <p>感谢注册<a href="http://{}/user/user_confirm?code={}" target=blank>http://{}</a>，\
                                    这里是我的博客，专注于Python和Flask、Django技术的分享！</p>
                                    <p>请点击站点链接完成注册确认！</p>
                                    <p>此链接有效期为{}天！</p>
                                    '''.format(settings.DOMAIN, code, settings.DOMAIN, settings.CONFIRM_DAYS)
                    send_email(subject, text, authenticated_user.email)
                    return redirect(reverse('blog:user_index'))
                return redirect(reverse('blog:user_index'))
            except Exception:
                messages.error(request, '用户名或密码错误')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', context={'form': form})


def user_confirm(request):
    try:
        # 从网址里获取验证码
        code = request.GET.get('code')
        # 默认为未验证用户，根据验证码找到用户
        confirm = ConfirmString.objects.get(code=code)
        # 获取验证码生成日期
        created_time = confirm.created_time
        now = datetime.datetime.now()
        # 时间比对，验证码过期的话，删除验证码，要求重新注册
        if now > created_time + datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            return render(request, 'users/user_confirm.html')
        # 验证码有效，验证成功，转向用户中心
        else:
            confirm.user.confirmed = True
            confirm.user.save()
            confirm.delete()
            return redirect(reverse('blog:user_index'))
    except Exception as e:
        # 网址中不带验证码参数，转向到首页
        return redirect(reverse('blog:index'))


def register(request):
    if request.method == 'POST':
        # request.POST 是类字典数据结构，记录了用户提交的注册信息，在这里就是用户名（username）密码（password）邮箱（email），用这些数据实例化注册表单
        form = RegisterForm(request.POST)
        # 验证数据的合法性，包括使用在forms.py里的自定义方法
        if form.is_valid():
            # 如果提交数据合法，从表单的cleaned_data字典里取出数据
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            sex = form.cleaned_data['sex']
            # 创建新用户
            new_user = User.objects.create(username=username, password=make_password(password1), email=email, sex=sex)
            new_user.save()
            code = make_confirm_string(new_user)
            subject = '来自我的博客的注册确认邮件'
            text = '''
                            <p>感谢注册<a href="http://{}/user/user_confirm?code={}" target=blank>http://{}</a>，\
                            这里是我的博客，专注于Python和Flask、Django技术的分享！</p>
                            <p>请点击站点链接完成注册确认！</p>
                            <p>此链接有效期为{}天！</p>
                            '''.format(settings.DOMAIN, code, settings.DOMAIN, settings.CONFIRM_DAYS)
            send_email(subject, text, email)
            # 对用户进行登录，login()的参数是HttpRequest对象和User对象，使用session框架把用户的ID保存到session中，匿名期间设定的session数据在用户登录后依然存在
            login(request, new_user)
            # 注册成功，跳转回首页
            return redirect(reverse('blog:index'))
            # 也可以return redirect('user_index')，其中user_index是views.py中定义的函数
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', context={'form': form})


# 如果未登录的用户请求装饰器 @login_required 的保护页面，将重定向到settings.py中的LOGIN_URL指定的URL
# login_required装饰器不检查用户的is_active值
@login_required
def user_index(request):
    """用户中心首页"""
    return render(request, 'users/index.html')


@login_required
def logout_view(request):
    """注销用户"""
    # logout()的参数是HttpRequest对象，没有返回值，即使用户未登录，使用logout()函数仍然不报错
    logout(request)
    return redirect(reverse('blog:index'))


def index(request, page=1):
    object_list = Post.published.all()
    # 每页10篇文章
    paginator = Paginator(object_list, 10)
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        # 页码不是数字，跳转到第1页
        post_list = paginator.page(1)
    except EmptyPage:
        # 页码超过最大页数，跳转到最后一页
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html', {'page': page, 'post_list': post_list})


# class IndexView(ListView):
#     queryset = Post.published.all()
#     # model = Post
#     template_name = 'blog/index.html'
#     context_object_name = 'post_list'
#     paginate_by = 10

def detail(request, pk):
    sent = False
    # 先获取被评论的文章，因为后面需要把评论和被评论的文章关联起来
    # 使用get_object_or_404，作用是当获取的文章（Post）存在时则获取；否则返回404页面给用户
    post = get_object_or_404(Post, pk=pk)
    # 阅读量 +1
    post.increase_views()
    # 获取这篇 post 下的全部评论
    form = CommentForm()
    comment_list = post.comment_set.order_by('-created_time')
    new_comment = None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # 如果表单数据没有通过验证，cleaned_data只包含验证通过的字段
            cd = form.cleaned_data
            # request.build_absolute_uri根据get_absolute_url创建http://开头的绝对地址
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '文章 "{}" 有新评论'.format(post.title)
            text = '你好：\n{}(邮箱{})在文章 "{}" 网址({}) 评论内容：\n {}'.format(cd['name'], cd['email'], post.title, post_url, cd['text'])
            send_email(subject, text, settings.EMAIL_RECIPIENTS)
            # 发送邮件后sent标记为已发送
            sent = True
            # 检查到数据是合法的，调用表单的save方法保存到数据库，commit=False的作用是仅仅利用表单的数据生成Comment模型类的实例，但不保存评论数据到数据库
            new_comment = form.save(commit=False)
            # 将评论和被评论的文章关联起来
            new_comment.post = post
            # 最终将评论数据保存进数据库，调用模型实例的save方法
            new_comment.save()
            # 重定向到post的详情页，当redirect函数接收模型的实例时，它会调用模型实例的get_absolute_url方法，然后重定向到get_absolute_url方法返回的URL
            return redirect(post)
    # 根据当前post获取当前文章的tags，然后返回这些tags的id，values_list根据'id'返回元祖，flat=True将元祖展开为列表
    post_tags_ids = post.tags.values_list('id', flat=True)
    # 根据所有的tag的id返回文章结果，并排除当前文章
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # 这里的'tags'是模型里面的字段名，Count('tags')统计标签数量并赋值给same_tags，降序排列，按照共同标签数量、发表时间降序排列
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created_time')[:4]
    return render(request, 'blog/detail.html',
                  {'post': post, 'comment_list': comment_list, 'form': form, 'similar_posts': similar_posts,
                   'new_comment': new_comment, 'sent': sent})


def detail_slug(request, year, month, day, slug):
    post = get_object_or_404(Post, slug=slug, status='published', created_time__year=year, created_time__month=month, created_time__day=day)
    comment_list = post.comment_set.all()
    new_comment = None
    sent = False
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '文章 "{}" 有新评论'.format(post.title)
            text = '你好：\n{}(邮箱{})在文章 "{}" 网址({}) 评论内容：\n {}'.format(cd['name'], cd['email'], post.title, post_url, cd['text'])
            send_email(subject, text, settings.EMAIL_RECIPIENTS)
            sent = True
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comment_list': comment_list, 'form': form, 'new_comment': new_comment, 'sent': sent})


# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class CategoryView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, name=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# def archives(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year, created_time__month=month).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class ArchivesView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year, created_time__month=month)


def redirect_url(request, shortcode):
    qs = Post.objects.filter(shortcode=shortcode).first()
    # return redirect(qs.true_url, permanent=True)
    return render(request, 'blog/redirect_url.html', locals())


def search(request):
    if request.method == 'POST':
        q = request.POST['q']
        return redirect(reverse('blog:search_result', args=[q, 1]))
        # redirect('blog.search_result', args=[q])


def search_result(request, q, page=1):
    # icontains表示包含且不区分大小写，Q 对象用于包装查询表达式，提供复杂的查询逻辑
    # Q(title__icontains=q) | Q(body__icontains=q) 表示标题或正文含有关键词q
    # 注意：如果使用title__icontains=q, body__icontains=q，将变成标题且正文含有关键词q的意思！！
    object_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    paginator = Paginator(object_list, 10)
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/search_result.html', locals())


class TagView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, name=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)
