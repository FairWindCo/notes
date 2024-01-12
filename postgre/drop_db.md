
# Видалення БД до якої ісеують з'єднання

Опитати представлення `pg_stat_activity` та отримати звідти значення pid сесій які потрібно прибити, далі завершити сессії `SELECT pg_terminate_backend(pid int)`.

## PostgreSQL 9.2 та вище:
```
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'TARGET_DB' -- ← change this to your DB
  AND pid <> pg_backend_pid();
```

## PostgreSQL 9.1 та нижче:
```
SELECT pg_terminate_backend(pg_stat_activity.procpid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'TARGET_DB' -- ← change this to your DB
  AND procpid <> pg_backend_pid();
```

## PostgreSQL 13 з'вилася опція FORCE

```
DROP DATABASE db_name WITH (FORCE);
```

DROP DATABASE drops a database ... Also, if anyone else is connected to the target database, this command will fail unless you use the FORCE option described below.
FORCE Attempt to terminate all existing connections to the target database. It doesn't terminate if prepared transactions, active logical replication slots or subscriptions are present in the target database.

[за інформацією](https://stackoverflow.com/questions/5408156/how-to-drop-a-postgresql-database-if-there-are-active-connections-to-it)
