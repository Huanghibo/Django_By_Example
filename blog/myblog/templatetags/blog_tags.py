from datetime import datetime
from django.utils import timezone
from django import template
from django.db.models.aggregates import Count
from ..models import Post, Category, Tag, Comment

register = template.Library()


@register.filter(name='time_since')
def time_since(value):
    """
    time距离现在的时间间隔
    1. 如果时间间隔小于1分钟以内，那么就显示“刚刚”
    2. 如果是大于1分钟小于1小时，那么就显示“xx分钟前”
    3. 如果是大于1小时小于24小时，那么就显示“xx小时前”
    4. 如果是大于24小时小于30天以内，那么就显示“xx天前”
    5. 否则就是显示具体的时间 2017/10/20 16:15
    """
    if isinstance(value,datetime):
        now = timezone.now()
        timestamp = (now - value).total_seconds()
        if timestamp < 60:
            return "刚刚"
        elif timestamp >= 60 and timestamp < 60*60:
            minutes = int(timestamp / 60)
            return "%s分钟前" % minutes
        elif timestamp >= 60*60 and timestamp < 60*60*24:
            hours = int(timestamp / (60*60))
            return "%s小时前" % hours
        elif timestamp >= 60*60*24 and timestamp < 60*60*24*30:
            days = int(timestamp / (60*60*24))
            return "%s天前" % days
        else:
            return value.strftime("%Y/%m/%d %H:%M")
    else:
        return value


@register.simple_tag
def total_posts():
    # 总文章数
    return Post.published.count()


@register.simple_tag
def get_recent_posts(num=5):
    # 最近5篇文章
    return Post.objects.all().order_by('-created_time')[:num]


@register.simple_tag
def get_recent_comments(num=5):
    # 最新5条评论
    return Comment.objects.all().order_by('-created_time')[:num]


@register.simple_tag
def archives():
    # 按照发表时间，按月降序排列
    return Post.objects.dates('created_time', 'month', order='DESC')


@register.simple_tag
def get_tags():
    # 只显示在该tag下文章数大于0的tag，num_posts属性可在模板引擎中使用
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_categories():
    # 只显示在该分类下文章数大于0的分类，num_posts属性可在模板引擎中使用
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_most_commented_posts(count=5):
    # 评论数最多的5篇文章
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.simple_tag
def get_most_views_posts(count=5):
    # 访问量最多的5篇文章
    return Post.published.order_by('-views')[:count]
