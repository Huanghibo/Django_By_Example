from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from common.decorators import ajax_required
from actions.utils import create_action
from actions.models import Action


# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             # 可以定义多个认证后台，Django 内部会逐一调用这些后台的 authenticate 方法来验证用户提供登录凭据的合法性，一旦通过某个后台的验证，表明用户提供的凭据合法，从而允许登录该用户。
#             # 当使用authenticate()函数，Django 会通过每一个定义在AUTHENTICATION_BACKENDS 中的后台一个接一个地尝试认证用户，直到其中有一个后台成功的认证，该用户才会停止进行认证。
#             # 只有所有的后台都无法进行用户认证，才不会在你的站点中通过认证。
#             # 使用 authenticate() 方法在数据库对用户进行认证，如果用户认证成功则返回用户对象，否则是 None 。
#             user = authenticate(username=cd['username'], password=cd['password'])
#             if user is not None:
#                 # 检查用户是否是激活状态
#                 if user.is_active:
#                     # login() 方法将用户设置到当前session中然后返回成功消息
#                     login(request, user)
#                     return redirect(reverse('account:dashboard'))
#     else:
#         form = LoginForm()
#     return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileEditForm(data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            # User 模型的set_password() 方法将用户的原密码进行加密后再保存
            new_user.set_password(user_form.cleaned_data['password'])
            # modelform才有save方法
            new_user.save()
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            create_action(new_user, '注册成功')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileEditForm()
    return render(request, 'account/register.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def edit(request):
    if request.method == 'POST':
        # request.user是UserEditForm这个ModelForm的模型User的实例，ModelForm才有instance=这个参数
        user_form = UserEditForm(instance=request.user, data=request.POST)
        # request.user.profile是Profile模型的实例，用户详细信息表单，包括上传的文件，ImageField使用request.FILES获取
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '资料更新成功')
        else:
            messages.error(request, '资料更新失败，请检查各字段是否符合要求')
    else:
        user_form = UserEditForm(instance=request.user)
        try:
            # instance=request.user.profile 查询数据库中已存在的用户详细信息，如果查询不到会报错RelatedObjectDoesNotExist
            profile_form = ProfileEditForm(instance=request.user.profile)
        except Exception:
            profile_form = ProfileEditForm()
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


# login_required 装饰器（decorator）会检查当前用户是否通过认证，如果用户通过认证，它会执行装饰的视图（view）
# 如果用户没有通过认证，它会把用户重定向到带有名为 next 的 GET 参数的登录 URL，该 GET 参数保存的变量为用户当前尝试访问的页面 URL
@login_required
def dashboard(request):
    # 当前的用户被设置在request对象中，可以通过使用request.user在模板中访问用户信息，未认证的用户在request中被设置成 AnonymousUser 的实例
    # 除自己以外所有用户的动态
    actions = Action.objects.exclude(user=request.user)
    # 根据request.user获取following，然后返回这些following的id，values_list根据'id'返回元祖，flat=True将元祖展开为列表
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # 如果用户正在关注他人，获取用户所关注的人的动态
        # select_related()方法允许取回关联对象，该方法将会转化成单独的、更加复杂的查询集，但是存取这些关联对象时可以避免额外的查询
        # select_related()方法是给ForeignKey（一对多）和OneToOne（一对一）字段使用的，通过在SELECT语句中执行SQL JOIN并且包含关联对象的字段实现
        # 使用user__profile(双下划线)实现在单独的SQL查询中连接profile表，如果调用select_related()而不传入任何参数，会取回所有ForeignKey关系的对象
        # select_related()无法给ManyToMany（多对多）或者倒转ForeignKey（多对一）字段使用，prefetch_realted方法在select_related()方法支持的关系上增加支持多对多和多对一的关系
        # prefetch_related()方法为每种关系执行单独的查询然后对各个结果进行连接，还支持对GeneriRelation和GenericForeignKey的预读
        actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related(
            'target')
    # 如果用户没有关注任何人，获取最新10条除自己外所有人的动态，不使用order_by()，因为已经在Action模型的Meta中设置过排序规则
    actions = actions[:10]
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


# 查询用户，is_active表示账户是否可用
@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})


# 查询用户详细信息，当通过传入的用户名无法找到用户，视图会返回HTTP 404响应
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})


# 因为用户的多对多关系使用定制的中间模型，所以ManyToManyField管理器默认的add()和remove()方法将不可用
# 使用Contact模型来创建和删除用户关系，本函数仍然使用user_detail视图的模板
@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            # 如果AJAX发送的是follow
            if action == 'follow':
                # get_or_create方法先查询，如果未查询到则创建
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, '关注了', user)
            # 如果AJAX发送的是unfollow
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})
