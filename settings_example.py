# Скопируйте этот файл в settings.py и заполните своими данными

SECRET_KEY = 'your-secret-key-here'
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_system_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5434',
    }
}
