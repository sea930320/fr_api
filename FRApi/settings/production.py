from .common import *

ALLOWED_HOSTS = ['34.82.119.147']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

HOST = 'localhost'
DB_NAME = 'frapi_2019'
DB_USER = 'root'
DB_PWD = 'Qwerty12#'

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': HOST,
        'PORT': '3306',
        'USER': DB_USER,
        'PASSWORD': DB_PWD,
        'NAME': DB_NAME,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}