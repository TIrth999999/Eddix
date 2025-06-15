import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'pgl5v)d#c$f%$oohe#8q9@w^_+yr#m1cmb0g@@&$sfty%=o1_c'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'editor',
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

ROOT_URLCONF = 'Eddix.urls'

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

WSGI_APPLICATION = 'Eddix.wsgi.application'
ASGI_APPLICATION = 'Eddix.asgi.application'

password = 'AVNS_Qk1mDoi-Zbm5g3w2stT'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD': password,
        'HOST': 'eddix-tirthgajera12345-0000.b.aivencloud.com',
        'PORT': '16597',
        'OPTIONS': {
            'ssl': {
                'ssl-mode': 'REQUIRED',
            }
        },
    }
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["rediss://default:AbpDAAIjcDEzMzY2ODk0NzJjOTE0Y2ViYjc5M2ViMWMyMjU2MzhlMHAxMA@maximum-mantis-47683.upstash.io:6379"],
        },
    },
}
# Static files (CSS, JS, etc.)
STATIC_URL = '/static/'

# Where collectstatic will place files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise will serve files from STATIC_ROOT
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'