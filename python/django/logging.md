
Якщо потрібні детальні логи про роботу DJANGO то додаємо в конфіг проекту:
```
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```
Такі налаштування будуть призводити до виводу на консоль всіх SQL запитів, при встановленні в конфігі DEBUG в значення True (during development).

[За мотивами](https://www.neilwithdata.com/django-sql-logging)
