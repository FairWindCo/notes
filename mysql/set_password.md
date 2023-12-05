*Встановлення пароля для користувача MySQL*
В загальгому вигляді:
```
SET PASSWORD [FOR user] auth_option
    [REPLACE 'current_auth_string']
    [RETAIN CURRENT PASSWORD]

auth_option: {
    = 'auth_string'
  | TO RANDOM
}
```
Приклад:
```
SET PASSWORD FOR 'jeffrey'@'localhost' = 'auth_string';
```
