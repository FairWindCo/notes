
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
В цьому випадке на консолі побачимо, щось таке:
```(0.000) SELECT "catalog_author"."id", "catalog_author"."first_name", "catalog_author"."last_name", "catalog_author"."date_of_birth", "catalog_author"."date_of_death" FROM "catalog_author" WHERE "catalog_author"."id" = 1 LIMIT 21; args=(1,)```

Додатково вказується час виконання запиту.

[За мотивами](https://www.neilwithdata.com/django-sql-logging)
