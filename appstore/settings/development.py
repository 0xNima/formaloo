import os

DEBUG = True


PAGE_SIZE = 10


if os.getenv('LITE_DB', '').lower() == 'no':
    DATABASES = {
        'default': {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.getenv('DB_HOST'),
            "USER": os.getenv('DB_USER'),
            "NAME": os.getenv('DB_NAME'),
            "PASSWORD": os.getenv('DB_PASS'),
            "PORT": int(os.getenv('DB_PORT')),
        }
    }
