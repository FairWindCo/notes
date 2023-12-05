
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

Додатково є ще варіант:
https://stackoverflow.com/questions/1074212/how-can-i-see-the-raw-sql-queries-django-is-running


## Можна отримати додаткові можливості з Django-extensions
[Django-extensions](https://pypi.org/project/django-extensions/) має команду shell_plus в якої є параметр print-sql

```./manage.py shell_plus --print-sql```
В середені щела маємо такий вивід:
```
User.objects.get(pk=1)
SELECT "auth_user"."id",
       "auth_user"."password",
       "auth_user"."last_login",
       "auth_user"."is_superuser",
       "auth_user"."username",
       "auth_user"."first_name",
       "auth_user"."last_name",
       "auth_user"."email",
       "auth_user"."is_staff",
       "auth_user"."is_active",
       "auth_user"."date_joined"
FROM "auth_user"
WHERE "auth_user"."id" = 1

Execution time: 0.002466s [Database: default]

<User: username>
```

## Додаткова консоль розробника django-debug-toolbar
[django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
```python -m pip install django-debug-toolbar```

Необхідні умови для роботи:
Обов'язково налаштування статичних файлів
```
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    # ...
]

STATIC_URL = "static/"
```
Та встановлення необхідного модуля:

```
INSTALLED_APPS = [
    # ...
    "debug_toolbar",
    # ...
]
```



