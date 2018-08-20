"""
Django settings for bookmarks project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ag11iv@va(2y!0x18(5)tjy2i=ic%=zj-8kaiz$15eye6yh-xg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'account',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'social_django',
    'images',
    'sorl.thumbnail',
    'actions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookmarks.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookmarks.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# 使用mysql做为数据库
import pymysql

pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookmarks',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

# 设置项目和后台语言，en-us是美式英语，en-gb是英式英语，在USE_I18N=True的情况下才生效
LANGUAGE_CODE = 'zh-hans'
# 设置本地时区
TIME_ZONE = 'Asia/Shanghai'
# 翻译系统是否启动
USE_I18N = True
# 本地格式化是否启动
USE_L10N = True
# 日期和时间是否是timezone-aware，如果设置为True，则所有的存储和内部处理甚至包括直接print显示全都是UTC时区，只有通过模板进行表单输入/渲染输出的时候，才会执行UTC和本地时间的转换
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# 将admin管理后台的jss 和css等静态文件拷贝到配置文件中的STATIC_ROOT目录下
# 然后将STATICFILES_DIRS 列表中所有目录下的内容也拷贝到STATIC_ROOT目录下，对外提供“/static”（STATIC_URL）为访问URL
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# MEDIA_URL 是管理用户上传的多媒体文件的主 URL，展示在网页上
MEDIA_URL = '/media/'
# MEDIA_ROOT 是多媒体文件在本地保存的路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

from django.urls import reverse_lazy

# 告诉 Django 用户登录成功后如果 contrib.auth.views.login 视图没有获取到 next 参数将会默认重定向到哪个 URL
LOGIN_REDIRECT_URL = reverse_lazy('account:dashboard')
# 重定向用户登录的 URL，使用urls.py中定义的命名空间
LOGIN_URL = reverse_lazy('account:login')
# 重定向用户退出的 URL
LOGOUT_URL = reverse_lazy('account:logout')

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# 是否使用TLS安全传输协议
EMAIL_USE_TLS = False
# 是否使用SSL加密，QQ企业邮箱要求使用
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.126.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'dstwhk@126.com'
EMAIL_HOST_PASSWORD = 'HK1107sina'
DEFAULT_FROM_EMAIL = 'dstwhk@126.com'
# 邮件提醒的发件人和收件人列表
EMAIL_SENDER = 'dstwhk@126.com'
EMAIL_RECIPIENTS = ['dstwhk@126.com']
# 确认码有效时间
CONFIRM_DAYS = 1

# 自定义认证后台，添加邮件认证后台、社交网站认证后台
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'account.authentication.EmailAuthBackend',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
)

# Facebook应用编号，集成Facebook登录的网址必须是https://开头
SOCIAL_AUTH_FACEBOOK_KEY = '2023326911252885'
# Facebook应用Secret
SOCIAL_AUTH_FACEBOOK_SECRET = '0ae517dc185ac23edb272adc725cb2d7'
# 从Facebook获得额外的权限，默认情况下不发送电子邮件，必须申请email许可才能获取
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
# Github应用Key
SOCIAL_AUTH_GITHUB_KEY = '425fe9305f97a987faec'
# Github应用Secret
SOCIAL_AUTH_GITHUB_SECRET = '3033e9032a32b588876016aeb3f034c405711e26'
# Twitter应用Key，服务器要能连接api.twitter.com
SOCIAL_AUTH_TWITTER_KEY = 'tgASiSWpS3uP4vOi7V35Behsl'
# Twitter应用Secret
SOCIAL_AUTH_TWITTER_SECRET = 'YT721zrwz14HGPvjlERmR43RJ8TGS3IODSw1fP7qoY1F3CULPg'
# Google客户端ID，要求必须是用域名申请，而且服务器要能连接accounts.google.com
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1089060095453-f4ear433e21gd2scueetqcsi486uk9en.apps.googleusercontent.com'
# Google应用Secret
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'o-IM8X4TB3ERynb7TAM3Hew2'

# 为所有下面设置的模型动态添加get_absolute_url()方法，将"app名.模型名"映射到接受模型对象并返回其URL的函数的字典，比如
# ABSOLUTE_URL_OVERRIDES = {
#     'blogs.weblog': lambda o: "/blogs/%s/" % o.slug,
#     'news.story': lambda o: "/stories/%s/%s/" % (o.pub_year, o.slug),
# }
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: reverse_lazy('account:user_detail', args=[u.username])
}

# Redis设置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
