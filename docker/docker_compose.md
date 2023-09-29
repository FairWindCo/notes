
# Приклад файлу docker-compose.yml
```
version: '2'

services:
  web:
    build:
    # build from Dockerfile
      context: ./Path
      dockerfile: Dockerfile
    ports:
     - "5000:5000"
    volumes:
     - .:/code
  redis:
    image: redis
```
В файлі є розділ build, що виконується під час процесу побудови образу (це специфічні дії, які необхідні для запуску образу, наприклад генерація сертифікату).

## Основні команди
### Запуск та зупинка образу
docker-compose start
docker-compose stop
### Поставити та зняти образ з паузи
docker-compose pause
docker-compose unpause
### Перелік запущених образів
docker-compose ps

docker-compose up
docker-compose down

# Довідка
## Сбірка образу

```
web:
  # build from Dockerfile
  build: .
  args:     # Add build arguments
    APP_HOME: app
```

## Створення образу з вказаного файлу Dockerfile
```
  build:
    context: ./dir
    dockerfile: Dockerfile.dev
```

## збірка з образу
```
  image: ubuntu
  image: ubuntu:14.04
  image: tutum/influxdb
  image: example-registry:4000/postgresql
  image: a4bc65fd
```

# Інші опції
## створення сервісу як розширення ісеуючого
```
  extends:
    file: common.yml  # optional
    service: webapp
```
## підключення дискових ресурсів (папок з хост ноди)
```
    volumes:
    - /var/lib/mysql
    - ./_data:/var/lib/mysql
```

## автоматичний перезапуск container
```
  restart: unless-stopped
```  
інші варіанти опцій: always, on-failure, no (default)

 # Порти
```
    ports:
    - "3000"
    - "8000:80"  # host:container
```

## expose ports to linked services (not to host)
  expose: ["3000"]

# Environment variables

## environment vars
```
  environment:
    RACK_ENV: development
  environment:
    - RACK_ENV=development
```
## environment vars from file
```
  env_file: .env
  env_file: [.env, .development.env]
```

# Commands
## command to execute
```
  command: bundle exec thin -p 3000
  command: [bundle, exec, thin, -p, 3000]
```
## override the entrypoint
```
  entrypoint: /app/start.sh
  entrypoint: [php, -d, vendor/bin/phpunit]
```

# Dependencies

## makes the `db` service available as the hostname `database` (implies depends_on)
```
  links:
    - db:database
    - redis
```
## make sure `db` is alive before starting
```
  depends_on:
    - db
```

## make sure `db` is healty before starting and db-init completed without failure
```
  depends_on:
    db:
      condition: service_healthy
    db-init:
      condition: service_completed_successfully
```

# Advanced features
```
  Labels
  services:
  web:
    labels:
      com.example.description: "Accounting web app"
```

# Перевірка стану контейнеру (Healthcheck)
## declare service healthy when `test` command succeed
 ```     
    healthcheck: 
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 1m30s
      timeout: 10s
      retries: 3
      start_period: 40s
```
# Тома (Volume)
## mount host paths or named volumes, specified as sub-options to a service
 ``` 
  db:
    image: postgres:latest
    volumes:
      - "/var/run/postgres/postgres.sock:/var/run/postgres/postgres.sock"
      - "dbdata:/var/lib/postgresql/data"

volumes:
  dbdata:
```

# Визначення DNS серверів для контейнерів
```
services:
  web:
    dns: 8.8.8.8
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

# Додавання Hosts в контейнер
```
services:
  web:
    extra_hosts:
      - "somehost:192.168.1.100"
```

# Зовнішні мережі (External network)
# приєднання до існуючої мережі (join a pre-existing network)
```
networks:
  default:
    external:
      name: frontend
```
# Пристрої
```
services:
  web:
    devices:
    - "/dev/ttyUSB0:/dev/ttyUSB0"
```
# Зовнішні зв'язки (External links)
```
services:
  web:
    external_links:
      - redis_1
      - project_db_1:mysql
```
# Мережа 
## створення власної мережі з назвою `frontend`
```
networks:
  frontend:
```
# Користувач
## визначення користувача від імені якого функціонує процесс
```
user: root
```
## визначення користувача за ідентифікатором користувача і групою
```
user: 0:0
```
