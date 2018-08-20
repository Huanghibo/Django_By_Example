import redis
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ImageCreateForm
from .models import Image
from common.decorators import ajax_required
from actions.utils import create_action
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


@login_required
def image_create(request):
    """    View for 使用JavaScript Bookmarklet创建Image    """
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, '收藏图片', new_item)
            messages.success(request, '新增图片成功！')
            # 跳转到绝对地址（图片详情页），因为这是modelform，所以可以直接使用模型中定义的get_absolute_url()方法
            # 实际上在模型中定义的get_absolute_url()方法就是reverse到详情页视图
            return redirect(new_item.get_absolute_url())
    else:
        # 用bookmarklet提供的数据填充表单
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


@login_required
def image_list(request):
    images = Image.objects.all()
    # 每页8张图片
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # 如果是AJAX请求，而且请求的页数超出范围，返回空的HTTP响应，在客户端停止AJAX分页
            return HttpResponse('')
        # 如果请求的页数超出范围，返回最后一页
        images = paginator.page(paginator.num_pages)
    # 如果是AJAX请求
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # 图片浏览数+1，incr()从1开始增加值，返回键的值，如果键不存在，值默认为0
    # 对Redis的键命名的惯例是使用冒号进行分割以创建键的命名空间，键的名字将特别冗长，在它们的名字中有关联的键会分享部分相同的模式
    total_views = r.incr('image:{}:views'.format(image.id))
    # zincrby()为有序集image_ranking的成员image.id的score值加上增量1
    r.zincrby('image_ranking', image.id, 1)
    return render(request, 'images/image/detail.html', {'section': 'images', 'image': image, 'total_views': total_views})


@ajax_required
@login_required
# require_GET装饰器只允许GET请求访问这个视图，require_POST装饰器只允许POST请求，以及可传递一组请求方法作为参数的require_http_methods装饰器
# 如果不满足条件，装饰器返回HttpResponseNotAllowed对象（状态码405），本函数仍然使用image_detail视图的模板
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            # 查找图片
            image = Image.objects.get(id=image_id)
            # 如果AJAX发送过来的是喜欢
            if action == 'like':
                # 根据图片反向关联获取用户，可使用add、remove、clear方法来添加关联对象、删除关联对象、删除所有关联对象集
                # 调用add()时传递存在于关联模型中的对象集不会重复添加这个对象，调用remove()时传递不存在于关联模型中的对象集也不会执行任何操作
                image.users_like.add(request.user)
                create_action(request.user, '喜欢', image)
            # 如果AJAX发送过来的是不喜欢
            else:
                image.users_like.remove(request.user)
                # 返回的都是带有application/json内容类型的HTTP响应（JSON输出）
                return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})


@login_required
def image_ranking(request):
    # 获取图片排行字典前10位，zrange返回有序集image_ranking中指定区间(0,-1表示整个有序集)内的成员，其中成员的位置按score值递增排序，具有相同score值的成员按字典序排列，desc=True表示成员的位置按score值递减排序
    # 下标参数start和stop都以0为底，0表示有序集第一个成员，1表示第二个成员，-1表示最后一位成员，-2表示倒数第二个成员
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # 获取浏览次数最多的图片，list()函数强制转化查询集为对象列表
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    # 根据对象的id在image_ranking_ids中的索引进行排序(lambda x中的x指代的是most_viewed)（因为image_detail视图存储的是Image实例的id），返回对象列表
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})
