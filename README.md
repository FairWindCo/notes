# IT Нотатки та Документація

Цей репозиторій містить колекцію технічних нотаток та документації з різних IT тематик. Матеріали організовані за категоріями для зручного пошуку та використання.

## 🐧 Linux та Система

### Керування часом
- **Тема**: Налаштування та синхронізація системного часу в Linux
- **Файл**: [`linux/time-management.md`](https://github.com/FairWindCo/notes/blob/main/linux/time-management.md)
- **Опис**: Команди та конфігурації для роботи з часовими зонами, NTP, systemd-timesyncd

### SSH через HTTP проксі
- **Тема**: Налаштування SSH з'єднань через проксі сервери
- **Файл**: [`linux/ssh-proxy.md`](https://github.com/FairWindCo/notes/blob/main/linux/ssh-proxy.md)
- **Опис**: Конфігурація SSH клієнта для роботи через HTTP/HTTPS проксі

## 🐍 Python

### Встановлення Python 3.12
- **Тема**: Інсталяція та налаштування Python 3.12
- **Файл**: [`python/python-3.12-installation.md`](https://github.com/FairWindCo/notes/blob/main/python/python-3.12-installation.md)
- **Опис**: Покрокові інструкції встановлення Python 3.12 на різних системах

### Оновлення пакетів
- **Тема**: Управління Python пакетами та залежностями
- **Файл**: [`python/package-management.md`](https://github.com/FairWindCo/notes/blob/main/python/package-management.md)
- **Опис**: pip, poetry, conda - методи оновлення та управління пакетами

## 🗄️ Бази Даних

### MySQL
- **Тема**: Встановлення паролів та налаштування безпеки MySQL
- **Файл**: [`databases/mysql-security.md`](https://github.com/FairWindCo/notes/blob/main/databases/mysql-security.md)
- **Опис**: Створення користувачів, встановлення паролів, налаштування прав доступу

## 🐳 Docker та Контейнеризація

### Docker Compose
- **Тема**: Робота з багатоконтейнерними додатками
- **Файл**: [`docker/docker-compose.md`](https://github.com/FairWindCo/notes/blob/main/docker/docker-compose.md)
- **Опис**: Конфігурація, запуск та управління службами через docker-compose

## ☸️ Kubernetes

### Томи зберігання
- **Тема**: Управління даними в Kubernetes кластері
- **Файл**: [`kubernetes/storage-volumes.md`](https://github.com/FairWindCo/notes/blob/main/kubernetes/storage-volumes.md)
- **Опис**: PersistentVolume, PersistentVolumeClaim, StorageClass

### Безпека Kubernetes
- **Тема**: Налаштування безпеки в Kubernetes
- **Файл**: [`kubernetes/security.md`](https://github.com/FairWindCo/notes/blob/main/kubernetes/security.md)
- **Опис**: RBAC, Network Policies, Pod Security Standards

### GrayLog в Kubernetes
- **Тема**: Розгортання системи логування GrayLog
- **Файл**: [`kubernetes/graylog-cluster.md`](https://github.com/FairWindCo/notes/blob/main/kubernetes/graylog-cluster.md)
- **Опис**: Встановлення та конфігурація GrayLog в Kubernetes кластері

## 🌐 Web Розробка

### Django
- **Тема**: Логування SQL запитів в Django
- **Файл**: [`django/sql-logging.md`](https://github.com/FairWindCo/notes/blob/main/django/sql-logging.md)
- **Опис**: Налаштування детального логування запитів до бази даних

## 📁 Структура Репозиторію

```
notes/
├── linux/
│   ├── time-management.md
│   └── ssh-proxy.md
├── python/
│   ├── python-3.12-installation.md
│   └── package-management.md
├── databases/
│   └── mysql-security.md
├── docker/
│   └── docker-compose.md
├── kubernetes/
│   ├── storage-volumes.md
│   ├── security.md
│   └── graylog-cluster.md
├── django/
│   └── sql-logging.md
└── README.md
```

## 🤝 Використання

Кожен файл містить:
- Детальні інструкції та приклади
- Команди для копіювання
- Посилання на додаткову документацію
- Примітки про поширені проблеми та їх вирішення

## 📝 Додавання нових нотаток

При додаванні нових матеріалів:
1. Створіть відповідну папку, якщо її ще немає
2. Дотримуйтесь структури назв файлів
3. Оновіть цей README.md з посиланнями на нові файли
4. Додайте теги та ключові слова для пошуку

---

*Останнє оновлення: Червень 2025*