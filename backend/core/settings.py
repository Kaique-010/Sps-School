from ctypes import cast
from email.policy import default
from pathlib import Path
from decouple import config  
from django.utils.timezone import timedelta
import os


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')
INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    'autenticacao',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'central_treinamentos',
    'tkts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='*').split(',')
CORS_ALLOW_ALL_ORIGINS = True  # Para desenvolvimento
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-cnpj',
    'x-username', 
    'x-email',
    'x-cpf',
    'x-Docu',
    'x-Empresa',
    'x-EmpresaID',
    'x-Filial',
    'x-FilialID',
    'x-Entidade',
]
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Araguaina'
USE_TZ = False
USE_I18N = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações do Django REST Framework com otimizações
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        #'Licencas.authentication.CustomJWTAuthentication',  # Autenticação customizada
        #'Entidades.authentication.EntidadeJWTAuthentication', 
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',        
        'rest_framework.parsers.FormParser',       
        'rest_framework.parsers.MultiPartParser',  
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,  # Otimizado para performance
    'MAX_PAGE_SIZE': 250,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=150),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
   
    "AUTH_HEADER_TYPES": ("Bearer",),        
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION", 
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'SPS API',
    'DESCRIPTION': 'Documentação da API para o sistema SPS',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
    },
    'ENUM_NAME_OVERRIDES': {
        'PatchedMobileSpsUserRequestStatusEnum': 'MobileSpsUserRequestStatusEnum',
        'PatchedMobileSpsUserRequestTypeEnum': 'MobileSpsUserRequestTypeEnum',
        'ClientEnum': 'core.utils.ClientEnum',
    },
    
}
# Configurações de E-mail
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST') 
EMAIL_PORT = int(config('EMAIL_PORT'))
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Patch para SMTP
import smtplib

orig_starttls = smtplib.SMTP.starttls

def starttls_patch(self, *args, **kwargs):
    # Remove keyfile e certfile se passados para evitar erro
    if 'keyfile' in kwargs:
        del kwargs['keyfile']
    if 'certfile' in kwargs:
        del kwargs['certfile']
    return orig_starttls(self, *args, **kwargs)

smtplib.SMTP.starttls = starttls_patch



SPECTACULAR_SETTINGS = {
    'TITLE': 'Mobile SPS API',
    'DESCRIPTION': 'Documentação da API do Mobile SPS',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
    },
    'POSTPROCESSING_HOOKS': [],
    'ENUM_NAME_OVERRIDES': { 
        'ClientEnum': 'core.utils.ClientEnum',
    },
}


CSRF_TRUSTED_ORIGINS = ["https://sps-training.site", "https://www.sps-training.site", "http://localhost:8000", "http://127.0.0.1:8000"]
ALLOWED_HOSTS = ["sps-training.site", "www.sps-training.site", "localhost", "127.0.0.1"]

CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

