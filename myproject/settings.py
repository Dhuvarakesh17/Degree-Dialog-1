from pathlib import Path
import environ
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9a+03g4i@+ydfhyb(&-+=5&zdm-tf8@2am4%#)=&6a*55(cch-'

DEBUG = True  # Turn OFF for production

ALLOWED_HOSTS = [
    
    "*.azurewebsites.net",
    "degree-dialog-1.onrender.com",
    "localhost",
    "127.0.0.1"
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'myapp',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Place this as high as possible
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

# CORS setup to allow frontend requests
CORS_ALLOWED_ORIGINS = [
    
    "https://degree-dialog-1.vercel.app",  # ✅ Your Vercel frontend
    "http://localhost:5173",               # Local development
    "http://127.0.0.1:5173",               # Local development alternate
]

# Allow Azure wildcard via regex
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.azurewebsites\.net$",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
CORS_ALLOW_HEADERS = ["*"]

ROOT_URLCONF = 'myproject.urls'

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

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database - SQLite for Django internals
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validators
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Load API key from .env
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("Missing COHERE_API_KEY in environment variables")

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
