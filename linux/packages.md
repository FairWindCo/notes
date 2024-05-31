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


# Встановлення пакету вказанної версії
```
apt-get install package=version
```
[https://askubuntu.com/questions/428772/how-to-install-specific-version-of-some-package]


# Помилка з пакетом
маємо таку помилку:
```
Preparing to unpack .../nodejs_0.10.28-1chl1~trusty1_amd64.deb ...
Unpacking nodejs (0.10.28-1chl1~trusty1) over (0.10.25~dfsg2-2ubuntu1) ...
dpkg: error processing archive /var/cache/apt/archives/nodejs_0.10.28-1chl1~trusty1_amd64.deb (--unpack):
 trying to overwrite '/usr/share/man/man1/node.1.gz', which is also in package nodejs-legacy 0.10.25~dfsg2-2ubuntu1
dpkg-deb: error: subprocess paste was killed by signal (Broken pipe)
Processing triggers for man-db (2.6.7.1-1) ...
Errors were encountered while processing:
 /var/cache/apt/archives/nodejs_0.10.28-1chl1~trusty1_amd64.deb
E: Sub-process /usr/bin/dpkg returned an error code (1)
```
Виправленння
```
sudo dpkg -i --force-overwrite /var/cache/apt/archives/nodejs_0.10.28-1chl1~trusty1_amd64.deb
```
В більш загальному варіанті
`sudo dpkg --remove --force-remove-reinstreq <packagename>`

[https://askubuntu.com/questions/525088/how-to-delete-broken-packages-in-ubuntu]

# Помилка при роботі з репозиторіями
маємо наступну помилку
```
Error:
 
Reading package lists... Done
E: Release file for http://security.ubuntu.com/ubuntu/dists/focal-security/InRelease is not valid yet (invalid for another 18h 32min 20s). Updates for this repository will not be applied.
E: Release file for http://archive.ubuntu.com/ubuntu/dists/focal-updates/InRelease is not valid yet (invalid for another 18h 32min 19s). Updates for this repository will not be applied.
E: Release file for http://archive.ubuntu.com/ubuntu/dists/focal-backports/InRelease is not valid yet (invalid for another 18h 32min 45s). Updates for this repository will not be applied.
```
перевіряємо час
`date`
виконуємо команду:
`sudo hwclock --hctosys`
якщо вона не працьовує то встановлюємо службу часу та часовий пояс
```
sudo apt install ntp
sudo dpkg-reconfigure tzdata
```
перезапускаємо службу часу
`sudo service ntp restart`
Крім того є тимчасовий варіант:
`sudo apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update`
[https://www.how2shout.com/linux/fix-inrelease-is-not-valid-yet-invalid-for-another-h-min-s-updates-for-this-repository-will-not-be-applied/]
