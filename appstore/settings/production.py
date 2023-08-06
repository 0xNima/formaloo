import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

SECRET_KEY = 'django-insecure-un3m(ofo&c4q_zy+)naps+uxol(h(!rz0dx=b60@ufb5rqp99$'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv('DB_HOST'),
        "USER": os.getenv('DB_USER'),
        "NAME": os.getenv('DB_NAME'),
        "PASSWORD": os.getenv('DB_PASS'),
        "PORT": int(os.getenv('DB_PORT')),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.getenv('LOG_FILE', 'access.log'),
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000"
]

CORS_ALLOW_CREDENTIALS = True


JWT_SECRET = SECRET_KEY
