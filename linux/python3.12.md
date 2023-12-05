# Встановлення Python 3.12 на Ubuntu
оновлюємо дистрибутив та спики пакетів
```sudo apt update && sudo apt upgrade -y```


додаємо репозиторій
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```
Двимося чи з'явиввся Python 3.12 в переліку пакетів
```apt list | grep python3.12```

Встановлюємо
```sudo apt install python3.12```


Якщо треба створюємо нове віртуальну оточення
```python3.12 -m venv env```

Якщо треба робимо аліаси в баші
```
echo "alias py=/usr/bin/python3" >> ~/.bashrc
echo "alias python=/usr/bin/python3" >> ~/.bashrc
```
## Встановлення за замовченням

Може заламати роботу дистрибутива
Ставимо альтернативи та приорітети до них
```
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 2
```
Дивимося сконфігуровані пріорітети
```sudo update-alternatives --config python3```



[На основі цієї статті](https://cloudbytes.dev/snippets/upgrade-python-to-latest-version-on-ubuntu-linux)


