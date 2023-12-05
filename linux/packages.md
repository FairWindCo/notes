# Особливості роботи з репозиторіями 


Коли треба отримати відбиток ключа для авторизації репозиторію:
```
gpg -v --keyserver hkps://keys.mailvelope.com --keyserver-options http-proxy=http://fw01.bs.local.erc:8080 --recv-keys 0x3D1A0346C8E1802F774AEF21DE8B853FC155581D
```
- *--keyserver* - вказує на сервер, де зберігаються ключі
- *--recv-keys* - номер ключа який треба отримати
- *--keyserver-options http-proxy=* - вказує на проксі сервер який треба використати.

Старий варіант для авторизації репозиторію, зараз вважається застарілим:
```
apt-key adv --keyserver https://keys.mailvelope.com --recv-keys 0xDE8B853FC155581D
```

Іще один варіант, отримання сертифікату:
```
curl -sSL \
'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xBBEBDCB318AD50EC6865090613B00F1FD2C19886' \
| sudo apt-key add -
```

- [source 1](https://stackoverflow.com/questions/68992799/warning-apt-key-is-deprecated-manage-keyring-files-in-trusted-gpg-d-instead)
- [source 2](https://unix.stackexchange.com/questions/361213/unable-to-add-gpg-key-with-apt-key-behind-a-proxy)
- [source 3](https://askubuntu.com/questions/732985/force-update-from-unsigned-repository)
