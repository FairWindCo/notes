# Перевірка змісту файлу
## Перевірка наявності того, що в файлі є певний рядок
```
- name: Ensure /tmp/my.conf contains 127.0.0.1
  ansible.builtin.lineinfile:
    path: /tmp/my.conf
    regexp: '^127\.0\.0\.1.*whatever'
    state: absent
  check_mode: yes
  changed_when: false
  register: out

- debug:
    msg: "Yes, line exists."
  when: out.found

- debug:
    msg: "Line does NOT exist."
  when: not out.found
```

## Ще один такий приклад
```
- ansible.builtin.lineinfile:
    path: /some/file
    regex: ".* bar baz"
    state: absent            # here's the trick
  changed_when: false
  check_mode: true
  register: result
  failed_when: result.found != 1
```

## Схожа повідінка до допомогою плагіна file.

Встановлення факту (змінної), що може буи використано в інших тасках.
```
- name: Check whether /tmp/my.conf contains "127.0.0.1"
  set_fact:
    myconf: "{{ lookup('file', '/tmp/my.conf') }}"  
  ignore_errors: yes

- name: Greet the world if /tmp/my.conf contains "127.0.0.1"
  debug: msg="Hello, world!"
  when: "'127.0.0.1' in myconf"
```

Важливо зрозуміти, що цей підхід може бути використаний і в секції змінних
```
- hosts: all
  vars:
     contents: "{{ lookup('file', '/etc/foo.txt') }}"
  tasks:
     - debug: msg="the value of foo.txt is {{ contents }}"
```


## Перевірка змісту файлу в умові до задачі.
```
- name: Greet the world if /tmp/my.conf contains "127.0.0.1"
  debug: msg="Hello, world!"
  when: "'127.0.0.1' in lookup('file', '/tmp/my.conf')"
```

## Інший варінт, за допомогою стандартних засобів linux
```
- name: Check whether /tmp/my.conf contains "127.0.0.1"
  command: awk /^127.0.0.1$/ /tmp/my.conf
  register: checkmyconf
  changed_when: False

- name: Greet the world if /tmp/my.conf contains "127.0.0.1"
  debug: msg="Hello, world!"
  when: checkmyconf.stdout | match("127.0.0.1")
```

# Вставка тексту до файлу

## Інше використання блоку lineinfile це додавання рядків до файлу, наприклад додати значення в конфіг:
```
    - name: Setup zabbix server for agent
      ansible.builtin.lineinfile:
        path: /etc/zabbix/zabbix_agent2.conf
        regexp: "^Server={{ zabbix_server }}"
        insertafter: "Server=127.0.0.1"
        line: "Server={{ zabbix_server }}"
      become: yes
      when: zabbix.changed
```


## Вставка блоку тексту в файл
```
- name: Insert/Update eth0 configuration stanza in /etc/network/interfaces
        (it might be better to copy files into /etc/network/interfaces.d/)
  ansible.builtin.blockinfile:
    path: /etc/network/interfaces
    block: |
      iface eth0 inet static
          address 192.0.2.23
          netmask 255.255.255.0
```

# Перезавантаження серверу
## Перезавантаження сервера з очікуванням
```
    - name: Reboot the Debian or Ubuntu server
      reboot:
        msg: "Reboot initiated by Ansible due to kernel updates"
        connect_timeout: 5
        reboot_timeout: 300
        pre_reboot_delay: 0
        post_reboot_delay: 30
        test_command: uptime
      when: reboot_required_file.stat.exists
```


## Очікування на перезавантаження серверу:

З використанням вбудованоно модуля для Ansible >= 2.7 (released in Oct 2018):
```
- name: Wait for server to restart
  reboot:
    reboot_timeout: 3600
```
Для версії Ansible < 2.7
```
- name: restart server
  shell: 'sleep 1 && shutdown -r now "Reboot triggered by Ansible" && sleep 1'
  async: 1
  poll: 0
  become: true
```
Це запускає команду оболонки як асинхронне завдання, тому Ansible не чекатиме завершення команди. 
Зазвичай параметр async дає максимальний час для виконання завдання, але оскільки для опитування встановлено значення 0, Ansible ніколи не здійснюватиме опитування, якщо команда завершена – це зробить цю команду «запустити й забути». 
Режим сну до та після завершення роботи покликаний запобігти розриву з’єднання SSH під час перезапуску, коли Ansible все ще підключено до вашого віддаленого хосту.

### Інший варіант очікування доступності серверу, як завдання:
```
- name: Wait for server to restart
  local_action:
    module: wait_for
      host={{ inventory_hostname }}
      port=22
      delay=10
    become: false
```

Можливо замість імені зосту можливо доречним буде використання змінних {{ ansible_ssh_host }} та {{ ansible_ssh_port }} для доступу по SSH:
Причому в в файлі інвентарізаціх можна зробити запис такого типу:
`hostname         ansible_ssh_host=some.other.name.com ansible_ssh_port=2222`

Ця задача запускає wait_for на машині де працює Ansible. Таким чином буде відбуватися очікування того, що буде відкрито 22 на віддаленому хості, задача буде розмочата з затримкою 10 секунд.

### Перезапуск та очікування в обробнику подій (handlers)

Варіант з використанням двох блоків як обробників подій, а не як завдання.
Для цього є 2 основні причини:

- повторне використання коду - ви можете використовувати обробник для багатьох завдань. Приклад: ініціювати перезапуск сервера після зміни часового поясу та зміни ядра,
- запускати лише один раз - якщо ви використовуєте обробник для кількох завдань, і більше ніж 1 із них вносять певні зміни => запускати обробник, тоді те, що виконує обробник, відбудеться лише один раз. Приклад: якщо у вас є обробник перезапуску httpd, підключений до зміни конфігурації httpd і оновлення сертифіката SSL, тоді у випадку змін конфігурації та сертифіката SSL httpd буде перезапущено лише один раз.

Очікування перезапуску в блоці обробки подій (handlers):
```
  handlers:

    - name: Restart server
      command: 'sleep 1 && shutdown -r now "Reboot triggered by Ansible" && sleep 1'
      async: 1
      poll: 0
      ignore_errors: true
      become: true

    - name: Wait for server to restart
      local_action:
        module: wait_for
          host={{ inventory_hostname }}
          port=22
          delay=10
        become: false
```

Ось приклад використання в задачі, наприклад при зміні імені хоста, що потребуж перезапуск
```
  tasks:
    - name: Set hostname
        hostname: name=somename
        notify:
          - Restart server
          - Wait for server to restart
```


Встановлення ядра linux-azure з перезавантаженням
```
    - name: Run the equivalent of "apt-get update" as a separate step
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600
      become: yes

    - name: Install the package "linux-azure"
      ansible.builtin.apt:
        name: linux-azure
      become: yes
      register: azure_result

   - name: Reboot a slow machine that might have lots of updates to apply
      ansible.builtin.reboot:
        reboot_timeout: 3600
      become: yes
      when: azure_result.changed
```

# Керування сервісами

## Запуск сервіса
```
    - name: Start service zabbix agent, if not started
      ansible.builtin.service:
        name: zabbix-agent2
        state: started
```
## Активація сервіса, під час завантадення системи.
```
    - name: Enable service zabbix agent, and not touch the state
      ansible.builtin.service:
        name: zabbix-agent2
        enabled: yes
```

# Оновлення серерів
## Оновлення серверів з перевіркою, що сервер потребує перезаватаження (в разі зміни ядра). Та зобороною цього роботи, якщо для хоста буде задана зміннна auto_reboot
```
    - name: Run the equivalent of "apt-get update" as a separate step
      ansible.builtin.apt:
        update_cache: yes
        cache_valid_time: 3600
      become: yes


    - name: Upgrade all apt packages
      apt: state=latest force_apt_get=yes
      become: yes


    - name: Update all Debian/Ubuntu packages to their latest version
      ansible.builtin.apt:
        name: "*"
        state: latest
      become: yes

    - block:
      - name: Check if a reboot is needed for Debian and Ubuntu boxes
        register: reboot_required_file
        stat: path=/var/run/reboot-required get_md5=no

      - name: Reboot the Debian or Ubuntu server
        reboot:
          msg: "Reboot initiated by Ansible due to kernel updates"
          connect_timeout: 5
          reboot_timeout: 300
          pre_reboot_delay: 0
          post_reboot_delay: 30
          test_command: uptime
        when: reboot_required_file.stat.exists
      when: auto_reboot is undefined
```
## Оновлення всіх пакетів:
```
   - name: Upgrade all apt packages
      apt: state=latest force_apt_get=yes
```
інший варіант
```
- name: Update all Debian/Ubuntu packages to their latest version
  ansible.builtin.apt:
    name: "*"
    state: latest
```
цікаві елементи: upgrade=latest - фактично еквівалент apt-get upgrade, force_apt_get=yes - вказує використати apt-get замість aptitude

```
      - name: Update all host/vm packages
        ansible.builtin.apt:
                update_cache: true
                cache_valid_time: 3600
                name: "*"
                state: latest
```
де: update_cache: true - запустить apt-get update,  cache_valid_time: 3600 - запустить apt лише, якщо cache_valid_time старше ніж 3600 секунд. name: "*" - вказує на всі пакети. state: latest - запуск apt-get upgrade.


# Робота зі змінними
```
tasks:
    - name: Run the command if "epic" or "monumental" is true
      ansible.builtin.shell: echo "This certainly is epic!"
      when: epic or monumental | bool

    - name: Run the command if "epic" is false
      ansible.builtin.shell: echo "This certainly isn't epic!"
      when: not epic


    - name: Run the command if "foo" is defined
      ansible.builtin.shell: echo "I've got '{{ foo }}' and am not afraid to use it!"
      when: foo is defined

    - name: Fail if "bar" is undefined
      ansible.builtin.fail: msg="Bailing out. This play requires 'bar'"
      when: bar is undefined      
```

# Залежності в ролях
В ролях можна вказати залежності від інших ролей, що робиться в файлі meta/main.yml ролі, та головне можна навіть передати зміні при вказанні залежності (остання залежність)
```---
# file: roles/stuartherbert.php-composer/meta/main.yml
dependencies:
- { role: stuartherbert.php-cli }
- { role: stuartherbert.php-json }
- { role: stuartherbert.git }
- { role: stuartherbert.redis-server, redis_server_instance: audit, redis_server_port: 6018 }
```


Скачування файлу
```
- name: Download nginx apt key
  get_url: 
    url: http://nginx.org/keys/nginx_signing.key 
    dest: /var/keys/nginx_signing.key
  register: aptkey
```
