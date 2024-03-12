# ansible
ansible - інструмент автоматизації (написаний на пітон). Реліз 2.7.0 до 2.7.6  - має баги.

- немає агента (по одній задачі за раз)
- стандартні протоколи для роботи на серверах
- сценарії на yaml
- кожний запуск повинен мати ідентичний результат (іденпатечність)
- багато сценаріїв

В цілому працює через SSH, але може підтримувати Windows (проте отребує додаткове налаштування самого Windows запустити ConfigureRemotingForAnsibe.ps1 та потребує PowerShell >= 3.0)
Здебільшого все що пишеться це файли в форматі YAML
Є великий репозиторій базових скриптів
Доступ до керованих серверів через SSH порт 22 або WinRM порт 5986


Потребує бібліотеку jinja2
може бути поставлений як через піп, так і через пакети ОС

Альтарнативи: CHEF, puppet, SALTSTACK (проте вони всі потребують встановлення агентів, де агенти переодично запитують центральний сервер на зміни які треба внести).
На відміну від них ансібл сам безпосередньо розсилає зміни.
В нього є платне розширення tower.

В практиці в якості контрольного сервера використовується сервер linux з пітоном. Цей сервер повинен мати доступ до керованих серверів.


# ВСТАНОВЛЕННЯ

Є багато варіантів встановлення дивитись тут:
(installing-and-upgrading-ansible)[https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible]

## На убунті:

### Встановлення через pipx:
`pipx install --include-deps ansible`

Встановлення додаткового розширення:

`pipx inject ansible argcomplete`

#### Оновлення:
`pipx upgrade --include-injected ansible`


### через  pip
встановлення:
`python3 -m pip install --user ansible`
#### оновлення:
`python3 -m pip install --upgrade --user ansible`


### перевірка версії:
`ansible --version`

# ПІДКЛЮЧЕННЯ ДО ХОСТІВ (ІНВЕНТАР)

Файл інвентарізації, це фактично перелік хостів до яких можливе підключення зазвичай він має назву hosts. Часто розміщений в окремому каталозі.

Крім файла hosts (або інша назва) до інвенторя ще належать дві папки host_vars та group_vars, що розміщені поруч.

Файл hosts:
```
[linux]
zabbix0101
zabbix0201
test1 ansible_host=xx.xxx.xxx.xx ansible_user=test_user ansible_pass=xxxxxxx
test2 ansible_host=xx.xxx.xxx.xx ansible_user=test_useransible_ssh_private_key_file=/path/to/key/file
[winserver]
new_win1 ansible_host=10.225.24.47 some_variable=100
new_win2 ansible_host=10.225.24.48
```
Один сервер займає одну строку. Часто розбивають на групи. В якості імені може бути ДНС ім'я, або просто назва в разі якщо буде застосовано ansible_host.
ansible_user дозволяэ задати ім'я користувача для підключення а ansible_pass задає пароль, хоче метод не рекомендований.
Крім того можно використати SSH ключ, тоді він задається параметром ansible_ssh_private_key_file, вказується путь до файлу.


файл має групи, що задані через "[назва групи]", в середені групи йде перелік хостів. Кожному хосту крім назви (ДНС ім'я) можна додатково задати змінні (як в пракладі для хоста new_win1).
ansible_host - якщо не прцює ДНС.

Якщо в каталозі host_vars створити файл з іменем zabbix0101, то всі змінні з цього файлу будуть задані при виконанні тасків для хосту zabbix0101 відповідно.
Приклад змісту такого файлу:
```
ansible_host: 10.225.24.48
some_variable: 200
```
Такий працює для всіх імен серверів (якщо в каталозі host_vars є файл з іменем серверу то він буде застосований).

Папка group_vars містить файли з назвами що співпадають з іменами груп (тоді такий файл буде застосований при роботі виконанні тасів для такої групи), а також каталог all.
all - це вбудована група, що означає всі хості з усіх груп, крім того всі файли з цієї папки будуть примінені завжи для будь якого хоста. (тут часто кладуть all.yaml)
ungrouped - це вбудована до якої віднесені всі сервери які не включені в жодну групу.

Назви груп регістро залежні, групи linux та Linux - це зовсім різні.

В самому файлі інвентаризації можна писати й севери без всяких груп. В якості запису або ІР

Крім того можна створювати групи які влючають в себе інші групи, в тому числі і вже згурповані групи. Наприклад:
```
[Group_1]
linux1
linux2

[Group_2]
linux3
linux4
10.10.2.3

[All_Group:children]
Group_1
Group_2

[All_Special:children]
All_Group
other_group

[All_Special:vars]
ansible_user = test
```

Таким чином група All_Group буде включати в себе всі сервери з груп Group_1 та Group_2. А група All_Special всі хости з All_Group та ще хости з other_group. Крім того додатково можна для груп задавати значення змінних, як в прикаді для групи All_Special.

Хоча всі змінні краще виносити в окремі файли ( host_vars та group_vars ).
Проте професійно блоки типу `[All_Special:vars]` виносити в окремі файли з назвами, що співпадають з назвою групи в папці group_vars. (важливо зберігати регістр букв імен).
Тобто для прикладу все що є в блоці `[All_Special:vars]` переноситься в файл group_vars\All_Special (без всяких розирень, повне співпадіння імені з групою), що матиме такий зміст відповідно до прикладу (треба пам'ятати, що символ "=" замінюєтьс на ":"):

```
---
ansible_user: test	
```
Тоді всередені інвенторі файлу є тільки назви хостів та групи і це вважається професійним підходом.




Перевірити які групи прописані можна командою:
`ansible-inventory --list`
ця команда видаэ всі групи з чого вони сладаються та які змінні до них відносяться.

`ansible-inventory --graph`
команда будує граф груп та хостів


Для роботи з хостами Windows потрібно:
1. Встановити бібліотеку но мастер хост
	`sudo pip install "pywinrm>=0.3.0"`

2. Створити записи в файлі хост з додатковими параметрами (де назва групи winserver може бути любою)
```
[winserver]
new_win1 ansible_host=10.225.24.47
new_win2 ansible_host=10.225.24.48

[winserver:vars]
ansible_user = admin
ansible_password = xxxxxxx
ansible_port = 5986
ansible_connection = winrm
ansible_winrm_server_cert_validation = ignore
```
тут блок `[winserver:vars]` вказує на змінні, що спільні до всіх хостів з групи winserver
Ці змінні можна задати для кожного серверу окремо, проте групою значно зручніше.
Ось ці для windows обов'язкові:
```
ansible_port = 5986
ansible_connection = winrm
ansible_winrm_server_cert_validation = ignore
```

3. На всіх хостах до яких підключаєтесь запустити скрипт від адміна
[https://docs.ansible.com/ansible/latest/os_guide/windows_winrm.html]
[https://docs.ansible.com/ansible/latest/os_guide/windows_setup.html]
[https://docs.ansible.com/ansible/latest/os_guide/windows_usage.html]



# ЗАПУСК AD-HOCK
Запуск одиночних команд (не в скрипті)

Найпростіша тестова команда:

`ansible -a /bin/date localhost`
ця команда запустить вказану шел команду /bin/date на хості localhost

отримаємо такий вивід
```
[WARNING]: No inventory was parsed, only implicit localhost is available
localhost | CHANGED | rc=0 >>
Tue Dec 19 05:04:48 PM EET 2023
```
де маємо невелике попередження, ну і безпосередньо результат роботи команди

Друга тестова команда, задіює модуль setup, 
`ansible -m setup localhost`
```
[WARNING]: No inventory was parsed, only implicit localhost is available
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "10.241.24.17"
        ],
        "ansible_all_ipv6_addresses": [
            "fe80::21d:ddff:fe22:7"
        ],
        "ansible_apparmor": {
            "status": "enabled"
        },
..................................
```
в цьому випадку ми підключили модуль, але не дали йому жодних станів, тому ансібл підключиться до хоста і збере багато різної інформації про хост та виведе на екран. В подальшому ця інформація буде порівнюватися з необхідним заданим станом та прийматися дії, щодо її приведення до бажаного стану

Наступний приклад тестовий модуль ping, що буде запущено на хостах описаних в файлі hosts, в розділі (групі) winserver, під користувачем msy, та з паролем запитаним з консолі (-k)
`ansible -m ping -i hosts winserver -u msy -k`

Приклад:
файл hosts:
```
[linux]
zabbix0101
zabbix0201
[winserver]
new_win1 ansible_host=10.225.24.47
new_win2 ansible_host=10.225.24.48
```
(важливо замітити, що через ansible_host= можна задати ІР адресу сервера на яку потрібно підключатися)
команда: `ansible -m ping -i hosts linux -u admin_root -k`
```
SSH password:
zabbix0201 | FAILED! => {
    "msg": "Using a SSH password instead of a key is not possible because Host Key checking is enabled and sshpass does not support this.  Please add this host's fingerprint to your known_hosts file to manage this host."
}
zabbix0101 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Маємо наступний результат. Перший хост zabbix0201 не був відпрацьований, тому, що його SSH відбиток не відомий та не занесений то бази. На другому хості zabbix0101 модуль успішно віпрацював. (для того, щоб перший хост запрцював достатньо спробувати підключится до нього по ssh, командою ssh zabbix0201, та підвердити занесення відбитка в базу знайомих хостів).

Всі комани це завжди якийсь модуль.

В прикладах нижче викоритосвується інвентар hosts, команда виконується для групи linux, під користувачем admin_root, а пароль користувача запитується з консолі.
(це частина команди `-i hosts linux -u admin_root -k`)

Наприклад запуск модуля setup виведене інформацію про систему (ОС, архітектура, час на сервері, які інтерфейси налаштовані ібагато іншого)
`ansible -m setup -i hosts linux -u admin_root -k`
Причому потім ці змінні можуть бути використані в скриптах.

Модуль shell виконання команд, сама команда передаэться через параметр -a "команда".
`ansible -m shell -a "uptime" -i hosts linux -u admin_root -k`

Модуль command запускає каманду але без шелу, не будуть працювати змінні, перенаправлення потоків та команди шелу. В цілому запуск бінарників.
`ansible -m command -a "uptime" -i hosts linux -u admin_root -k`

Модуль copy копіювання файлів, наприклад копіює sorce_file в папку за шляхом dest_path та зразу змінює права доступу на 0644 (але ця частина не обов'язкова)
`ansible -m copy -a "src=sorce_file dest=dest_path/ mode=0644" -i hosts linux -u admin_root -k`
Цікавий момент модуля copy якщо файл вже інсує і має той же зміст, то зміни не будуть вноситься та в своємо звіті ansible відмітить, що такі зміни не будули внесені, що може потім в подальшому в скриптах використовуватися для пропуску чи виконання певних дій.

Модуль file - керування файлами, в прикладі файл sorce_file буде переведено в статус absent - тобто файл буде видалений:
`ansible -m file -a "path=sorce_file state=absent" -i hosts linux -u admin_root -k`
Цей же модуль як і модуль copy фіксує чи були внесені зміни.

Модуль get_url скачує файл за посиланням sorce_link та розміщує його за шляхом dest_path
`ansible -m get_url -a "url=sorce_link dest=dest_path" -i hosts linux -u admin_root -k`
Качає тільки якщо файл не існує або змінений.
	
Модуль yum відповідає за встановлення та видалення пакетів, наприклад встановлює пакет stress останньої версії. Для видалення state=removed
`ansible -m yum -a "name=stress state=latest" -i hosts linux -u admin_root -k`

Модуль uri робить підлкючення по http\https до вказанного url та видає код http, якщо треба контент то дадати опцію return_content=yes
`ansible -m uri -a "url=url" -i hosts linux -u admin_root -k`
`ansible -m uri -a "url=url return_content=yes" -i hosts linux -u admin_root -k`

Модуль service керує сервісами, наприклад запускається сервіс httpd, він переводиться в статус state=started, та акивується запуск при старті системи enabled=yes
`ansible -m service -a "name=httpd state=started enabled=yes" -i hosts linux -u admin_root -k`

(для команди ansible ключ -b значить виконати команду в режимі sudo)
для команди ansible ключ -v дає більше інформації (тільки ім'я файлу конфігу який використовує), ключ -vv вже більше інформації про сам ансібл, ключ -vvv - вже більше інфомації, строки конектів, користувачі, далі є ключі  -vvvv та -vvvvv де ще більше інформації.

Быльше про модулі
[https://docs.ansible.com/ansible/latest/collections/all_plugins.html#all-modules-and-plugins]

Корисне:
`ansible-doc -l` показує всі модулі, що є в ансібл з коротким описом.

`ansible-doc -l | grep win_ `  - видасть всі модулі, що призначені для windows систем.


# Правила формата YAML

Файл починаэться з комбынації "---"
Весь файл це тест.
До кожне значення в форматі ключ та значення або перелік (перелік починається з символа "-").
Головне збірагіти кількість пробілів на одному рівні. Для вкладених значень збільшується кількість пробілів. Сама кількість пробілів не має значення, має значення, щоб на одному рівні їх кількість була однаковою.
```
---
 - fruits:
   - apple
   - orange
   - mango

 - cars:
   - kia
   - ford
   - bmw

 - test:
     color: "red: color"
     value: active
     works:
       - list
       - manage

 - server: { name: test, room: near, os: windows, soft: ['chrome', 'photoshop'] }
 - looks: ['one', 'two']
```

В прикладі є два об'єкти fruits та cars які складаються зі списку значень. Крім того  є об'єкт test що має набір атрибутів color, value та works. Причому атрибут works являє собою список значень, а занчення атрибуту color взято в лапки, щоб екранувати символ ":". Крім того наведено приклад об'єкту server, що являє собою словник з парами ключ значення, причому ключ soft зберігає в середені себе список. Також наведно приклад спрощеного задання списку, це об'єкт looks.



# ЗАПУСК PLAYBOOK

Фактично в проді, існує playbook та файл інвентарізації. Тоді ансібл під час роботи бере команди з playbook та відправляє їх на хости з інвентарізації та виконує їх.
Сам по собі плейбук це комбінація команд, наче скрипт заданий в форматі yaml.
Завжди починається з блоку, "---", та стартує з назви блоку:

```
---
- name "назва плейбуку"
```

Важливо не використовувати символи "таб", бо будуть помилки.

Самий простий:
```
---
- name "test ping"
  hosts: all
  become: yes
  
  tasks:
  - name: "ping"
    ping:
```

Це фактично сценарій буде виконано на всіх серверах hosts: all, в режимі з підвищеними привілеями become: yes. Він складається з одного таска, який використає модуль ping.
Так як модуль ping немає параметрів то в нього нічого не задано, а саме "ping:". Фактично назва таска, що задається в значенні name, використовується для інформування користувача та не є обов'язковою, тобто name: "ping" можна було упустити. Ці значення які задані в name, буде видно у виводі команди яка виконує плейбук.


Для запуску плейбуків слугує команда: ansible-playbook
```
ansible-playbook [-h] [--version] [-v] [-k] [--private-key PRIVATE_KEY_FILE] [-u REMOTE_USER] [-c CONNECTION] [-T TIMEOUT]
                        [--ssh-common-args SSH_COMMON_ARGS] [--sftp-extra-args SFTP_EXTRA_ARGS] [--scp-extra-args SCP_EXTRA_ARGS]
                        [--ssh-extra-args SSH_EXTRA_ARGS] [--force-handlers] [--flush-cache] [-b] [--become-method BECOME_METHOD]
                        [--become-user BECOME_USER] [-K] [-t TAGS] [--skip-tags SKIP_TAGS] [-C] [--syntax-check] [-D] [-i INVENTORY] [--list-hosts]
                        [-l SUBSET] [-e EXTRA_VARS] [--vault-id VAULT_IDS] [--ask-vault-password | --vault-password-file VAULT_PASSWORD_FILES]
                        [-f FORKS] [-M MODULE_PATH] [--list-tasks] [--list-tags] [--step] [--start-at-task START_AT_TASK]
                        playbook [playbook ...]
```
Важливі ключі:
- --diff - дозволяє показати які зміни вніс таск
- --force-handlers - вказує виконувати хендлери незалежно від того успішно виконаний таск чи ні. Зачасту потребує в тому випадку, якщо хенделри повинні бути виконані незалежно від результатів тасків (наприклад перезапуск серверу).
- --inventory - коротка форма -i вказує на файл інвенторя
- --limit - можна вказати, що таски необхідно виконувати лише на певних серверах чи групах
- --step - пошагове виконання тасків (для наладки)
- --become - надо підвищувати привелеє при виконанні тасків на серверів
- --ask-pass - вказує запитати пароль (коротка форма -k)

Наприклад:

`ansible-playbook -i hosts play.yaml`

файл інвентаризації
```
[linux]
zabbix0101
zabbix0201

[linux:vars]
ansible_user=admin_root
ansible_password=ххххххххххх
ansible_sudo_pass=*****************
```

Файл плейбуку:
```
---
- name: test install mc
  hosts: linux
  remote_user: admin_root
  become: yes

  vars:
    app: mc
    site: index.html

  tasks:
    - name: install mc
      yum:
         name: {{ app }}
         state: present

    - name: copy site
      copy: src={{site}} dest=/var/www/
      notify: restart apache

  handlers:
  - name: restart apache
    service: name=httpd state=restarted 
```

Фактично відбудеться встановлення МС на вказані хости (або перевірка, що він там уже є)
Тут є перші цікаві елементи це змінні, що описують додаткові параметри до групи linux, а саме ansible_user, ansible_password вказуть на логін та проль під яким підключатися.
Їх можна замінити через опції -u <користувач>, та -k прочитати пароль з клавіатури.
Також тут вказано параметр ansible_sudo_pass, що задає пароль для підвищення привелеїв, можна задати пароль через запит з консолі параметр командної строки --ask-become-pass.
Стосовно самого плейбуку: сам по собі файл плейбуку може мати від одного до кількох блоків, кожен блок має свою назву, що задається name. hosts - задає групу на якій він буде застосований,  remote_user задає користувача під яким буде виконано всі команди блоку плейбуку. become: yes - вказує, що команди повинні бути виконані з підвищенними привелеями. Далі йде перелік тасків які будуть виконуватися - це розділ tasks. Кожна задача має свою назву, та безпосередньо свою команду, задіяну модуль yum, далі вже йдуть парамтри відповідно до модуля, в данному випадку вказується, що повинен бути пристуній пакет mc. На виході цей плейбук перевірить наявність пакету mc, та в разі його відсутності спробує його встановити.

Для цього плейбука створено блок vars, де задана змінна app в зачення mc. І ця змінна використана в параметрах для модуля yum.
Потім ці змінні в разі необхідності можна змінити та таким чином налаштовувати поведінку скрипту.
Крім того є розділ handlers які не виконуються якщо їх не визивали. Фактично handlers це тіж самі таски. Проте вони будуть виконані тільки тоді коли на них спрацює посилання notify, яке буде виконано всякий раз коли відповідна таска в якій він використаний успішно завершилася та внесла зміни. Таким чином таска "restart apache", буде виконана тільки якщо таска "copy site" завершилася успішно та дісно скопіювала файл. ВАЖЛИВО РОЗУМІТИ: копіювання може і не бути бо файл з таким змістом вже існує, тоді таска "restart apache" виконана не буде.
В розділі handlers також можуть застосовуватися умови when.


За замовченням для кожного таску відкривається нове окреме з'єднання. Проте є додатковий модуль mitogen, що змінює стратегію виконання. На цілевому сервері запускється процес, який приймає всі таски й починає їх виконувати. Його потрібно окремо встановити.
https://github.com/mitogen-hq/mitogen/blob/master/docs/ansible_detailed.rst
https://mitogen.networkgenomics.com/ansible_detailed.html


Необхідно скачати та розпакевати mitogen-0.3.5.dev0.tar.gz.

Змінити ansible.cfg:
```
[defaults]
strategy_plugins = /path/to/mitogen-0.3.5.dev0/ansible_mitogen/plugins/strategy
strategy = mitogen_linear
```

Загальні об'єкти плейбуку:
Task - перелік необхідниз задач які повинні бути виконані
Variables - змінні що використовуються в тасках та темплейтах, та можуть бути перезадані з командного рядка
Template - набори jinja темплейтів, для створення файлів на серверах (наприклад конфігів)
Handler - спеціалізовані задачі які виконуються в самому кінці (наприклад коли після змін конфігурації треба перезапустити сервер). Якщо зміни були бути виставлено спеціальний флаг і в разі його наявності буте виконано спеціальний таск хендлер.
Role - спеціалізований шаблон, що обєднує Task, Variables, Handler та Template та дозволяє логічно їх об'єднати крім того зручно поєднувати та перевикористовувати.


# ЗМІННІ
всередені ансібл змінні мають певний пріоретит і можуть бути задані в різних місцях. Значення з вищим пріоритетом замінюють всі з більш нижчим пріоритетом.

6. Найнижчий пріоритет міють змінні з папки role\defaults 

5. Наступний пріоритет це змінні, що записані в інвентарі для групи серверів типу:
```
[linux:vars]
ansible_user=admin_root
```

4. Наступний пріоритет це змінні записані безпосередньо в інвенторі, наприклад це ansible_host
```
[winserver]
new_win1 ansible_host=10.225.24.47
```
3. Наступний пріорітет це змінні інвентаря що розміщені в каталозі host_vars, тут розміщені файлікі зі зміннами, що застосовуються для кожного з серверів окремо

2. Змінні що задані в плейбук безпосередньо в розділі vars

1. Змінні що задані через командний рядок (ключ -e), вони мають найвищій приоритет (перекривають все крім констант).


Самі змінні можна подивитись, для цього використовується модуль debug.
Наприклад є такий плейбук:

```
---
- name: test variables
  hosts: all
 
  vars:
    message: test mes
    secret: password_xxxx

  tasks:
  - name: print variable
    debug:
      var: secret
  - debug: 
      msg: "this is secret {{ secret }}"

  - set_fact: new_variable="{{ message }} {{ secret }}"
  - debug: 
      var: new_variable

  - debug: 
      var: ansible_system

  - shell: uptime
    register: shell_result 
```

Такий плейбук надрукує занчення змінної secret та в другому таску ціле повідомлення з значенням змінної. Єдине що це повідомлення буде виконано для всіх хостів. Важливо розуміти, що тут можуть бути використані не тільки змінні які безпосередньо задані в плейбуку, а й такі що задані в інвенторі чи такі, що утворилися в наслідок роботи інших модулів чи початкового блоку збирання фактів, що забезпечує модуль setup (який за замовченням виконується автоматично та збирає інформацію про систему її стан та формує набір змінних які можна далі використовувати).

Модуль set_fact дозволяє створювати нові змінні, в нашому прикладі set_fact створює нову змінну new_variable значення якої формується з вже існуючих змінних. Це значення лише створюється і може бути використане але не буде надруковано. Для того, щоб його побачити в прикладі ми використали таск  debug, що йде слідом.

Інформацію про початкові факти, які збираються можна побачити через модуль setup (приклад його використання див. вище).

Крім того в прикладі показано вивід змінної ansible_system, що створюється модулем setup при початковому збиранні фактів про систему.

Ще одна особливість результати команд не будуть зберігатися. Наприклад команда uptime, не збереже своє значення. Для того, що отримати результат виводу використовуєтсья register, та вказується змінна яка буде містити результат (вивід команди). В нашому випадку все що видасть uptime буде збережено в shell_result.

В разі необхідності змінною може бути значення дериктиви hosts. Наприклад так:

```
---
- name: test variables
  hosts: {{ MYHOSTS }}
 
  vars:
    message: test mes
    secret: password_xxxx

  tasks:
  - name: print variable
    debug:
      var: secret
```

Тоді щоб виконати такий плейбук треба задати зовнішню змінну (це можна зробити наступними засобами):
`ansible-playbook playbook.yml -e "MYHOSTS=linux"`
`ansible-playbook playbook.yml --extra-var "MYHOSTS=linux"`
`ansible-playbook playbook.yml --extra-vars "MYHOSTS=linux"`
Тут -e --extra-var  та --extra-vars це однакові опції для передачі зовнішніх змінних.
Таким чном можна змінити значення будь якої змінної. Можна сразу задати кілька змінних:
`ansible-playbook playbook.yml --extra-var "MYHOSTS=linux  owner=DENIS"`
Таким чином всюди де зустрінеться змінна owner її значення буде замінено на DENIS. Це важливо зрозуміти, бо якщо наприклад для хостів зазначити змінну owner і вони будуть мати різні значення в кожного своя. То при задачі через консоль будуть перетерті занчення для всіх хостів на зазначене. 
Значення змінних задані в консолі мають найвищій пріорітет.


# БЛОКІ ТА УМОВИ

Іноді виникає необхідність в застосуванні різних модулів в залежності від обставин запуску. В простому прикладі для встановлення софта на ubuntu викоритосвуэться модуль apt, а для centos модуль yum.
Сім'ю для системи можна побачити через змінну ansible_os_family.

Наприклад маємо такий плейбук встановлення апач.
```
---
- name: setup & config apache
  hosts: all

  tasks:
  - name: install apache on RedHat
    yum:
      name: httpd
      state: latest

  - name: install apache on Debian
    apt:
      name: apache2
      state: latest
```

Якщо залишити так як описано, то завжди будуть помилки бо один з тасків не виконається так як немає відповідного пакетного менеджеру.
Тоді змінемо:
```
---
- name: setup & config apache
  hosts: all

  tasks:
  - name: install apache on RedHat
    yum:
      name: httpd
      state: latest
    when: ansible_os_family == "RedHat"

  - name: install apache on Debian
    apt:
      name: apache2
      state: latest
    when: ansible_os_family != "RedHat"
```
В такому випадку таски будуть виконуватися лише за умови, що вираз зазначений в when достовірний. 
Якщо кілька тасків залежать від умови то тоді використовується об'єднання в блоки.
```
---
- name: setup & config apache
  hosts: all

  tasks:
  - block:
    - name: install apache on RedHat
      yum:
        name: httpd
        state: latest
    - name: restart service
      service: name=httpd state=started
    when: ansible_os_family == "RedHat"

  - block:
    - name: install apache on Debian
      apt:
        name: apache2
        state: latest
    - name: apache2 service
      service: name=httpd state=started
    when: ansible_os_family != "RedHat"
```

В ціх фрагментах таски об'єднані в блоки та для всього блоку застосовується умова. Це корисно, щоб не писати умови для кожного таску окремо.


# ЦИКЛИ

Найпростіший обхід по списку значень:
```
---
- name: test variables
  hosts: all

  tasks:
  - debug: 
      msg: "this is item {{ item}}"
    with_items:
       - "One"
       - "Two"
       - "Five"

```
Цей таск виведе три строки, що будуть сформовані з наведеного списку.

```
---
- name: test variables
  hosts: all

  tasks:
  - name: "Loop"
    debug: 
      msg: "this is item {{ item}}"
    loop:
       - "One"
       - "Two"
       - "Five"

  - name: "Loop until"
    shell: echo -n Z >> myfile.txt && cat myfile.txt
    register: output
    delay: 2
    retries: 10
    until: output.stdout.find("ZZZZ")
```

Перший таск це також цикл, що обхожить список за елементами списку.

Другий таск ци цикл, що повторює команду модуля shell, реєструє її вивід в змінну output, так саме виконання відбудеться 10 разів (вказано параметр retries: 10, якщо його не вказати то за замовчанням 3 повтори - це максимально дозволена кількість повторів), з паузами між повторами  delay: 2 (якщо не вказати то пауз не буде). Контроль виходу з циклу на основі того, що в вихідних данних буде строка "ZZZZ". Тут варто зазначити, що цикл буде виконуватися до тих пір поки умова вказана в until не стане істиною, або спрацює обмеження на кілкість retries).

Розглянемо такий плейбук:
```
---
- name: setup & config apache
  hosts: all

  tasks:
  - block #block for RedHat
    - name: install apache on RedHat
      yum:
        name: httpd
        state: latest
    - name: restart service
      service: name=httpd state=started
    when: ansible_os_family == "RedHat"

  - block #block for Debian
    - name: install apache on Debian
      apt:
        name: apache2
        state: latest
    - name: apache2 service
      service: name=httpd state=started
    when: ansible_os_family != "RedHat"

  - name: Copy Files to server
    copy: src={{item}} dest=/var/www mode=0555
    loop: 
      - "img1.png"
      - "img2.png"      
      - "img3.png"
    notify:
      - Restart Apache RedHat
      - Restart Apache Debian

  - name: Create file
    copy:
      dest: /var/www/index.html
      content: |
         Line 1
         Line 2
         Line 3 {{ ansible_os_family }}

  handlers:
  - name: Restart Apache RedHat
    service: name=httpd state=restarted 
    when: ansible_os_family == "RedHat"

  - name: Restart Apache Debian
    service: name=apache2 state=restarted 
    when: ansible_os_family == "Debian"
```

Він встановлює Apache різними засобами в залежності від ОС, крім того відбувається копіювання файлів і в разі якщо воно відбулося дається команда на перезапуск сервіса Apache.
Тут використано цикл для копіювання багатьох файлів, що не писати багато тасків. Тут цікава частина, що вібдувається виклик двох handlers тасків. Проте буде виконано лише один, який буде відповідати занченню ansible_os_family. Цікаве застосування модуля copy, це створення файлу з контентом, можна застосувати атрибут content та вказати що повинно бути всередині файлу. Для коротких елементів це може бути зручніше ніж шаблон. 

Копіювання файлів може бути зроблено за шаблоном без безспосерднього задання імен, для цього таск копіювання можна змінити аким чином:
```  
  - name: Copy Files to server
    copy: src={{item}} dest=/var/www mode 0555
    with_fileglob: "*.png"
```
Тут відбудеться копіювання всіх файлів з розширенням .png.



# МОДУЛІ

основні модулі, що застосовуються
- yum_repository - модуль керування репозиторями для систем типу RadHat
- yum - модуль керування пакетами для систем типу RadHat
- template - модуль шаблонів (бере файл з каталогу шаблонів, проводить відповідні маніпуляції по встановленню значень зі мінних та записує на вказане місце на хості)
- service - модуль керування сервісами (запуск, зупинка).
- file - модуль керування файловою системою, створення файлів та папок, їх видалення
- sysetemd - модуль керування sysetemd, крім простих маніпуляцій з сервісами (старт\стоп) може виконувати deamon_reload:yes оновлення конфігурації самого sysetemd


include_tasks - виконується під час виконання тасків, може мати умову виконання
import_tasks - виконується завжди на єтапі завантаження плейбук

Є ще два модуля inlucde та import, які можуть бути застосовані всередині тасків:
```
---
- name: setup & config apache
  hosts: all

  tasks:
    - name: impoprt tasks
      import: some_file.yml

    - include: some_file.yml
```

При застосуванні import на етапі аналіза плейбуку відбувається вставка зовнішнього контенту, причому зразу відбувається підстановка всіх занчень змінних. Інша поведінка при include, в цьому випадку вставка відбувається лише тоді коли виконання доходить до відповідної директиви і в цем момент відбувається вставка.
Частіше використовується include.
Крім того можна перекидати змінні в середину фалів, що вставляється:
  tasks:
    - include: some_file.yml some_vaiable="value"
В цьому випадку буде вставлено зміст файлу some_file.yml, причому в середині цього файлу змінна some_vaiable буде мати значення "value".


with_items - цикл, виконає дії для всії елементів списку
register - створює стан таску і записується в вказану змінну (register: task_result), потім значення цих змінних може застосовуватися разом з when
Наприклад:
```
- name: "{{ mongo_db_service }} service init"
  template:
    src: "{{ mongo_db_service }}.service"
    dst: "/etc/systemd/system"
    mode: 0644
  register: mongodb_unit

- name:  "{{ mongo_db_service }} service restart"
  systemd:
     name: {{ mongo_db_service }}
     state: reloaded
     deamon_reload:yes
  when:
    - mongodb_unit.changed
```

Тут створюэться файл з шаблона і в разі якщо такий файл був створений чи змінений відбувається перезапуск сервісу.



# ШАБЛОНИ

Якщо нам потрібно не просто скопіювати файл як він є, один на одного а внести зміни, то нам допоможуть шаблони. Шаблон це файл заготовка всередені якого існує спеціальна мова розмітки яка дозволяє вивести значення змінних та керувати процесом формування файла. Загалом весь файл переноситься як є крім спеціальних значень які формують блоки керування та вивід змінних.
Сам файл шаблона має розщирення "j2".

Приклад шалона:
```
# THIS FILE IS ANSIBLE MANAGED
{% if mongodb_client is defined %}
{% for item in mongodb_client %}
{{ item|ipv4|ternary(item, '# ' ~ item) }}
{% endfor %}
{% endif %}
```
тут все що не влючено в душки {% %} чи {{  }} буде вставлено як є. Все що в {% %} це блоки керування, а {{  }} - вивід значень змінних. В пракладі є блок умовної перевірки if що перевіряє чи задана відповідна змінна, та блок циклу for що пробігає по списку да застосовую до кожного значення певні дії. В нашому випадку це вивід в файл.
Сам по собі вивід це теж можливе поєднання самого виводу з додатковмими фільтрами. В прикладі |ipv4 перевіряє що значення item це коректна адреса в форматі ІР версії 4, на виході перевірки тільки значення правда або не правда.  |ternary(item, '# ' ~ item) - оператор який на вході отримаууючи логічне значення вставить item якщо значення правда та '# ' ~ item - якщо ні.
Фактично всі не ipv4 значення будуть вставлені але закоментовані.

Для перенесення цього темплейта на сервер слугує модуль template, який використовується замість copy. Тоді таск матиме вигял на зразок:
```
  - name: Copy Files to server
    template: src=template.j2 dest=/etc/hosts mode=0555
```
Тут фактично відбудеться копіювання з перетворенням файлу template.j2 на сервер в файл /etc/hosts, всі конструкції мови шаблонів при копіюванні будуть замінені на відповідні значення.

# РОЛІ

Самі ролі завжди в папці roles (або в папці на яку вказано в конфігу ансібла).

Кожна роль - фізично це каталог на диску всередині якого є наступні папки та файл README.md:
- defaults  
- files  
- handlers  
- meta  
- tasks  
- templates  
- tests  
- vars
- README.md  

Фактично в кожній папці знаодиться файл main.yaml, а також можуть бути ціла купа інших (їх можна включати за допомогою команд).

- Каталог files знаходяться файли що без змін будуть копіюватися на сервер через метод copy
- Каталог templates містить шаблонні файли, що будуть застосовані модулем template з урахуванням всіх змінних.
- Каталог defaults містить змінні, що можна перезадати
- Каталог vars містить змінні, що не можуть бути перезадані (це константи).

Саму необхідну структуру можна створити командою
`ansible-galaxy init <назва ролі>`
виконання цієї команди створить папку з назвою "<назва ролі>", та відповідні під папки. Також будуть створені файли  main.yaml які будуть містити порожні заготовкию
Наприклад:
`ansible-galaxy role init inventory_update`

Наприклад умовного включення в разі наявності певної ролі:
```
- include_tasks: special_tasks.yaml
  when "'mongodb' in roles"
```
Підключить додаткові таски, але лише якщо в ролях задано mongodb.


Фактично плейбук можна перетворити в роль, наприкладі наступного:
```
---
- name: setup & config apache
  hosts: all

  tasks:
  - block #block for RedHat
    - name: install apache on RedHat
      yum:
        name: httpd
        state: latest
    - name: restart service
      service: name=httpd state=started
    when: ansible_os_family == "RedHat"

  - block #block for Debian
    - name: install apache on Debian
      apt:
        name: apache2
        state: latest
    - name: apache2 service
      service: name=httpd state=started
    when: ansible_os_family != "RedHat"

  - name: Copy Files to server
    copy: src={{item}} dest=/var/www mode=0555
    loop: 
      - "img1.png"
      - "img2.png"      
      - "img3.png"
    notify:
      - Restart Apache RedHat
      - Restart Apache Debian

  handlers:
  - name: Restart Apache RedHat
    service: name=httpd state=restarted 
    when: ansible_os_family == "RedHat"

  - name: Restart Apache Debian
    service: name=apache2 state=restarted 
    when: ansible_os_family == "Debian"
```

Тут всі таски з розділу tasks переносяться в tasks\main.yml, він буде містити наступне:
```
- block #block for RedHat
    - name: install apache on RedHat
      yum:
        name: httpd
        state: latest
    - name: restart service
      service: name=httpd state=started
  when: ansible_os_family == "RedHat"

- block #block for Debian
    - name: install apache on Debian
      apt:
        name: apache2
        state: latest
    - name: apache2 service
      service: name=httpd state=started
  when: ansible_os_family != "RedHat"

- name: Copy Files to server
  copy: src={{item}} dest=/var/www mode=0555
  loop: 
      - "img1.png"
      - "img2.png"      
      - "img3.png"
  notify:
      - Restart Apache RedHat
      - Restart Apache Debian
```

Всі handlers в handlers\main.yml він буде містити наступне:
```
- name: Restart Apache RedHat
  service: name=httpd state=restarted 
  when: ansible_os_family == "RedHat"

- name: Restart Apache Debian
  service: name=apache2 state=restarted 
  when: ansible_os_family == "Debian"
```
Всі зображення що ми пкопіювали повинні бути розміщені в папці files
Шаблон який ми використовували повинен бути розміщений в templates.

Причому в командах для модуля copy шлях завжди буде відраховуватися від папки files, а для templates шлях до шблона починається від папки templates.
Тобто при копіюванні якщо файл лежить безпосередньо в папці files, то ми вказуємо лише ім'я файла. А для шаблона, якщо він лежить в папці templates, то ми вказуємо лише назву шаблона, без додаткового уточнення шляху.

Таким чином якщо б ми створили роль apache_role, та відповідно рознесли всі частини як описано вище, то наш плейбук скоротився б до такого:
```
---
- name: setup & config apache
  hosts: all
  roles:
    - apache_role
```
В цілому ролі призначені для створення блоків для їх багаторазового використання.

Ролі можна застосовувати і за певними умовами:
```
---
- name: setup & config apache
  hosts: all
  roles:
    - { role: apache_role, when ansible_system == 'Linux' }
```
В прикладі роль apache_role буде застосована тільки якщо система на хості з сім'ї Linux.

# Делегування виконання тасків з плейбук


Можна окремо визначити що такс буде запущено на заздалегіть визначеному хості.

Наприклад:
```
---
- name: setup & config apache
  hosts: all

  tasks:
    - name: install apache on RedHat
      shell: echo "server to deregister {{ inventory_hostname }}, node name {{ ansible_nodename }} >> /home/log.txt
      delegate_to: zabbix0101

    - name: restart service
      service: name=httpd state=started
```
В цьому прикладі таск "install apache on RedHat" буде виконано на сервері zabbix0101, якщо такий даний таск буде виконуватися в плейбуці. Тобто коли виконання йде і доходить до таску з директивою delegate_to, то виконання цієї команди відбудеться на вказаному хості.
Наприклад в нас є кілька серверів і треба зробити їх дерегістрацію на централізованому ресурсі. Тоді робиться таск з delegate_to, і тоді всі сервери по черзі виконують команду на централізованому. Або можливі операції типу регітрації нових ресрусів.

Ще цікаве застосування перезавантаження серверів з очікуванням коли всі вони з'являться
```
---
- name: reboot and check
  hosts: all

  tasks:
    - name: install apache on RedHat
      shell: sleep 3 && reboot now
      async: 1
      pool: 0

   - name: wait for server up
     wait_for:
       host: "{{ inventory_hostname }}"
       state: started
       delay: 5
       timeout: 40
     delegate_to: 127.0.0.1
```
Сама команда ребут маэ досить специфічну конструкцію, по перше сама команда чекає кілька секунд перш ніж зробить ребут (якщо так не зробити то може виникнути помилка). По друге опції async та pool, вказують що команду треба запустити асінхронно та не очікувати її завершення. Без цих елементів можна отримати помилку яка виникне під час розриву з'єднання.
Друга таска буде очікувати коли хост опиниться в статусі started, перевірка почнеться через 5 секунд і максимальний час очікування 40 секунд. Так як ця команда буде виконана для кожного хоста, то ми дочекаємося доки всі перезавантажаться, так як самі сервери перезавантажуються то на них не можна чекати, доводиться чекати на хості ансібл (для цього тут вказано delegate_to: 127.0.0.1). Тобто важливо, що саме очікування відбувається на іншому хості який не задіяний перезавантаженням.

Якщо до таска додати атрибут run_once: true, то така таска буде запущена лише на одному хості.
```
---
- name: reboot and check
  hosts: all

  tasks:
    - name: install apache on RedHat
      shell: pg_dump >backup.tar.gz
      run_once: true
```
Така команда запуститься на першому сервері з переліку в інвенторі. Або якщо в поєднанн з delegate_to, то буде на вказаному сервері і один раз. Бо якщо без run_once опція delegate_to призведе до того, що таска до якої вона додана буде виконана стільки разів скільки хостів задіяно.

# ПЕРЕХОПЛЕННЯ ПОМИЛОК


За замовченням якщо якась таска призводить до помилки то всі наступні таски не запускаються, але це стосується лише того хоста на якому була помилка, якщо на інших помилок не було то там все продовже виконуватися. Але таку повідінку можна змітини.
Розглянемо простий плейбук:
```
---
- name: errors checks
  hosts: all

  tasks:
   - name: Task1
     yum: name: test_зззззз state-latest

   - name: Task2
     shell: echo "Hellow"

   - name: Task3
     shell: echo "World"
```
Так як Task1 встановлює пакет якого не існує, то всі інші таски виконані не будуть.
```
---
- name: errors checks
  hosts: all
  any_errors_fatal: true

  tasks:
   - name: Task1
     yum: name: test_зззззз state-latest
     ignore_errors: true

   - name: Task2
     shell: echo "Hellow"
     register: result
     failed_when: "'Fail' in result.stdout"

   - name: Task3
     shell: echo "World"
     register: res
     failed_when: res.rc == 0
```

Якщо додати до таски опцію  ignore_errors: true, то далі виконання буде продовжено навіть при наявності помилки.
Другий таск, реєструє вивід скрипту, та перевіряє його на наявність у виводі слова Fail. Тут є додаткова опція яка дозволяє визначати свій статус успішності команди на основі даних.
В данному випадку це наявність строки в стандартному виводі команди. А для того, щоб отримати доступ до стандартного виводу, доводиться заносити його в змінну, через register.
Третій таск перевіряє код повернення з команди шелу і якщо, вона дорівнює 0 то така команда вважається зламаною. Але тут для того, щоб отримати доступ до коду повернення треба результат команди занести в змінну.

Якщо в плебуку зазначено   any_errors_fatal: true то будь яка помилка призводить до повного зупинення плейбук, на всіх серверах. Це повна зупанка.


# НАЛАШТУВАННЯ  ansible

налаштування може бути задане через
1. ANSIBLE_CONFIG змінна оточення, що вказує де конфіг
2. ansible.сfg (в поточному каталозі)
3. ~/.ansible.сfg (в домашноьому каталозі)
4. /etc/ansible/ansible.сfg (глобальний кофіг)

порядок перевірки такий як вказано

в загальному плані тут можна побачити такі елементи:
```
[defaults]
timeout			=15			задає таймаут підключення
role_path		=./roles		задає катлог де будуть зберігатися ролі
remote_port		= 22			порт для підключення
become			= true			буде підвищувати права до адміна завжди
become_user		= root			користувач для підвищеня
fork			= 100			буде одночасно опрацбовувати 100 серверів (проте більше 15-20 серверів жре дуже багато пам'яті)
log_path		= ./ansible.log 	сюди складати логи
inventory		= invenotory/		шлях до інвенторя
host_key_cheking	=False			вимикає перевірку відбитків серверів (інкаще не пустить)
retry_files_enabled	=True			
stdout_callback		=debug			опція що дозволяю гарні повідомлення для дебагу

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=600s -o UserKnownHostFiles=/dev/null
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
```
Блок ssh_connection задає параметри для коннекту, крім того вказаний набір дозволяє трохи пришвидшити ансібл, якщо не застосовано mitogen

Конфіг бажано зберігати поруч з проектом.
Часто тут заразу прописують інвентар. Таким чином його не буде потрібно вводити.
Тоді запуск буде простіший: ansible all -m ping замість ansible -i hosts all -m ping, якщо inventory в ansible.сfg не заданий.

# НАЛАДКА

Лінтер перевірка ситаксису
[https://ansible.readthedocs.io/projects/lint/]
[https://github.com/ansible/ansible-lint]

Фремворк тестування
[https://ansible.readthedocs.io/projects/molecule/]
[https://github.com/ansible/molecule]

Ключи для відладки:
--syntax-check тільки перевірити ситаксис
--check режим коли таск виконується але змін на сервері не відбуваються (проте є проблеми якщо такси залежать від змін то такі частини не будуть працювати)
--diff  показати зміни що відбулися
--step  виконати по крокам

Записати в конфіг змінну
ansible.cfg
 stdout_callback = debug

Є ще додаткова третегія що дає змогу відладки плейбуків
Playbook strategy:debug

# ШИФРУВАННЯ
Можна зашифрувати плейбук, роль, інвентар, шаблон, або змінну (одну чи кілка).
Шифрація відбувається прозоро для користувача

Якщо щось зашифровано, то ансібл при старті просить вести пароль, а потім цим паролем він буде пробувати все розшифрувати

`ansible-vault encrypt <им'я файла, що необхідно зашиврувати>`

`ansible-vault encrypt file-name --vault-id dev@promt`
команда
`ansible-vault encrypt file-name`
створить зашифрований файл, спочатку вона запитає пароль для шифрації та дешифрації. Якщо файла немає то буде запущено редактор в якому можна набрати всі необхідні дані, після закриття редактора відбудеться автоматичне шифрування.

Подивитись зміст можна командою:
`ansible-vault view file-name`
Тут теж або треба буде ввести пароль, або його вкзати.


Редагувати зміст можна командою:
`ansible-vault edit file-name`
Тут теж або треба буде ввести пароль, або його вкзати.

Можна змінити пароль шфрування, для цього використовуєтсья команда:
`ansible-vault rekey file-name`
Тут теж або треба буде ввести старий та новий пароль, або вказати їх в команді.

Розшмфрувати файл
`ansible-vault decrypt file-name`

Крім шифрування цілих файлів можна зашиврувати кореме значення, для цього використовується команда для отримання зашифрованих значень, які потім вставляються замість значень:

`ansible-vault encrypt_string "this is sparta" --name encs --vault-id dev@file`

Загальні опції для утиліт що вказати пароль, або вимагати його вводу:

--ask-vault-pass - пароль для шфрування запитати з консолі
--vault-password-file - паоль для шифрування прочитати з файлу

Ці опції дають змогу задати кілька паролів (де є ідинтифікатор пароля та де його шукати):
--vault-id id@promt  	пароль з ідентфікатором id та запитом з консолі (файл з назвою promt)
--vault-id id@password_file  пароль з ідентфікатором id та зчитується з файлу password_file

Приклад
`ansible-vault encrypt playbook.yaml --vault-id dev@pass`
зашифрує файл playbook.yaml паролем який зчитає з файлу pass, паролю буде присвоєно ідентифікатор dev.
Це дозволяє використати декілька паролів для різних частин. Після шифрування файл буде мати спеціальний заголовок що вказує що файл зашифровано і там є ідентифікатор ключа.

Якщо запустити файл звичайним чином
`ansible-playbook -i red -u test -k playbook.yaml `
Після запиту пароля SSH отримаэ помилку, що немаэ ключів для секретів.

Щоб використати секрети треба змінити строку запуску так:
`ansible-playbook -i red -u test -k playbook.yaml --vault-id dev@pass`
тут вказано використовувати пароль з ідентифікатором dev та зчитати його з файлу pass

ПРИМІТКА:
тут є особливість поведінки за замовченням, якщо в нього є кілька ключів то він спочатку сробує розшифрувати тим в якого ідентифікатор співпадає, а потім пробує всі інші.
І в нашому тестовому випадку якщо запустити таке ansible-playbook -i red -u test -k playbook.yaml --vault-id d@pass, то все одно файл виконається.
Таку поведінку можна відключити, але потребує додаткових опцій.



# Динамічні Інвентарі AWS Amazon
Є деякі автоматичні системи, що працюють з хмарами та можуть з цих хмар формувати динамічні інвенторі файли
Опис того функціоналу можна знайти тут:
https://docs.ansible.com/ansible/latest/inventory_guide/intro_dynamic_inventory.html#intro-dynamic-inventory

Тоді деякі такі скрипти можуть бути використані в якості файлів інвенторі, а вони в свою чергу можуть отримувати перелік хостів прямо з конфігурації хмари і таким чином забезпечують автоматичне виконання скриптів на активному середовищі.

Також є можливість і динамічного створення хостів через ansible. Проте я сам так не робив.


