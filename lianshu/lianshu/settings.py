"""
Django settings for lianshu project.

Generated by 'django-admin startproject' using Django 2.0.5.

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
SECRET_KEY = 'nr$5crfsuou)b@%%&$*vj+k8@=yb#wvwyvk=k^l9u3&6l$_$i6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'lianshu_app.apps.LianshuAppConfig',
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

ROOT_URLCONF = 'lianshu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lianshu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# LOGGING_URL = '/log/'

# #logger
# LOGGING = { 
#     'version': 1, #指明dictConnfig的版本，目前就只有一个版本
#     'disable_existing_loggers': False,  #是否禁用所有的已经存在的日志配置
#     'formatters': { #格式器
#         'verbose': { #详细的格式器
#             # 时间  日志等级  路径  文件名 模块 函数名 报错行
#             'format': '%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d %(message)s' 
#             }, 
#         'simple': {    #自定义的格式器 仅有日志等级 消息内容
#             'format': '%(levelname)s %(message)s'
#             },
#         }, 
#         'handlers': { #处理器，
#             'console':{  #流处理器，所有的高于（包括）debug的消息会被传到stderr，
#                 'level':'INFO', 
#                 'class':'logging.StreamHandler', 
#                 'formatter': 'verbose' #使用的是verbose格式器  可选择自定义的'simple'
#                 }, 
#             'file': {    #文件处理器
#                 'level': 'INFO', 
#                 'class': 'logging.FileHandler', 
#                 'filename':  os.path.join(BASE_DIR+LOGGING_URL, "test.log"),  #相对路径 BASE_DIR为manage.py的路径
#                 'formatter': 'verbose' 
#                 }, 
#             'email': {   #邮件处理器
#                 'level': 'ERROR', 
#                 'class': 'django.utils.log.AdminEmailHandler', 
#                 'include_html' : True, 
#                 },
#             'logfile': {    #文件处理器
#                 'level': 'INFO', 
#                 'class': 'logging.FileHandler', 
#                 'filename':  os.path.join(BASE_DIR+LOGGING_URL, "15.log"),  #相对路径 BASE_DIR为manage.py的路径
#                 'formatter': 'simple' 
#                 }, 
#             }, 
#         'loggers': { #记录器
#             'django': {  #记录器的名字
#                 'handlers': ['console', 'file', 'email'], 
#                 'level': 'INFO', 
#                 'propagate': True, 
#                 },
#             '15':{
#                 'handlers': ['logfile'], 
#                 'level': 'INFO', 
#                 'propagate': True, 
#                 }
#             },
#         }

