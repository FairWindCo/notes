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
(lineinfile)[https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html]

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
(blockinfile)[https://docs.ansible.com/ansible/latest/collections/ansible/builtin/blockinfile_module.html]

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

# Виконання таску на визначеному сервері
Код вказаний нижче виконає команду на вказанному сервері, та поверне результат виконання у змінну. 
Параметр `run_once: true` вказує, що команда повинна виконатися лише один раз (навіть якщо плейбук виконується на кількох хостах, команда відпрацює лише на одному). delegate_to - вказує на машину де буде запущена команда. 
```
   - name: form join command
     ansible.builtin.command: "kubeadm token create --print-join-command"
     register: join_command
#       remote_user: "{{ my_remote_user }}"
     remote_user: admin_root
     run_once: true
     delegate_facts: true
     delegate_to: "{{ kuber_master_server }}"
```
Примітка: без remote_user в моємо прикладі команді підключалася під іменем користувача ansible. Проте використати в якості користувача змінну не вдалося (виникає помилка, що змінної не існує. Тому можна лише явно прописати користувача.
(tasts delegation)[https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html
(run once)[https://stackoverflow.com/questions/22070232/how-to-get-an-ansible-check-to-run-only-once-in-a-playbook]
Крім того є ще можливість передати зібрані файти на відалений хост (замість збору нових яке відбудеться при підключенні), для цього слугує параметр delegate_facts
## Виконання команд на ansible хості (локально)
```
в першому випадку просто відправляємо команду на 127.0.0.1
- name: Take out of load balancer pool
  ansible.builtin.command: /usr/bin/take_out_of_pool {{ inventory_hostname }}
  delegate_to: 127.0.0.1
```
Але для цього варіанту є спеціальна версія команди
```
- name: Take out of load balancer pool
  local_action: ansible.builtin.command /usr/bin/take_out_of_pool {{ inventory_hostname }}
```

# Копіювання локального файл (та встановлення прав)
тут є цікавий момент, перше якщо буде не вказано `remote_src: yes` то в якості `src` буде виступати локальна папка на хості де працює сам ansible. Проте якщо параметр remote_src таки встановлено то тоді src це вже папка на хості де виконується скрипт. 
Крім простого копіювання зразу встанолюються права на власника файлу.
Спеціальні змінні застосовані для того, щоб вказати на користувача під яким виконується скрипт на відаленому сервері.
```
- name: Copy config for {{ ansible_facts.user_id }} kubectl
  ansible.builtin.copy:
    src: /etc/kubernetes/admin.conf
    dest: "{{ ansible_facts.user_dir }}/.kube/config"
    remote_src: yes
    owner: "{{ ansible_facts.user_uid }}"
    group: "{{ ansible_facts.user_gid }}"
    mode: '0440'
  become: yes
```
(команда copy)[https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html]

# Встановлення кількох пакетів за раз
Якщо треба поставити кілька пакетів то це можно зробити так:
```
- name: Install required packages
  ansible.builtin.apt:
    pkg:
      - curl
      - gnupg2
      - software-properties-common
      - apt-transport-https
      - ca-certificates
  become: yes
```

# Приклад як додати ключ репозіторію та репозіторій
в мене був перший варінт видати команду шелу. Проте для себе почав використовувати інший варіант з скачуванням файла через команду get_url
```
- name: get containerd repository keyring
#  ansible.builtin.shell: curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmour -o /etc/apt/trusted.gpg.d/docker.gpg
  ansible.builtin.get_url:
    url: https://download.docker.com/linux/ubuntu/gpg
    dest: /etc/apt/trusted.gpg.d/containerd.asc
    mode: '0644'
    force: true
  become: yes
```
## Додавання самого репозиторію
В мене був також варіант через шел (наведено в коменті)
```
- name: add containerd repository
  ansible.builtin.apt_repository:
    repo: deb https://download.docker.com/linux/ubuntu jammy stable
    state: present
    filename: containerd
#  ansible.builtin.shell: add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  become: yes
```
# Приклад ітерації по змінній
(ітерації)[https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html]
```
- name: Show all the hosts in the current play
  ansible.builtin.debug:
    msg: "{{ item }}"
  loop: "{{ ansible_play_batch }}"
```
сама змінна може бути задана так:
```
ansible_play_batch:
  - item1
  - item2
```
# Заміна строки в файлі 
```
- name: Change config for containerd
  replace:
    dest: /etc/containerd/config.toml
    regexp: '[\s]*SystemdCgroup = false'
    replace: '\n           SystemdCgroup = true'
  tags: containerd-config
```

# Використання шаблона
Тут шаблон http-proxy.conf.j2 перетворюэться на файл /etc/systemd/system/containerd.service.d/http-proxy.conf, і зразу встановлюються права та власник.
Цей приклад взятий з ролі тому шаблон треба прозмістити в папці шаблонів.
```
- name: Setup proxy for containerd
  template: src=http-proxy.conf.j2 dest=/etc/systemd/system/containerd.service.d/http-proxy.conf  mode=0644 owner=root
```

# Запуск та активація служби
state: started - задає стан служби який необхідний. Крім started є ще інші статуси (restarted - перезапуск, stoped - завершено)
enabled: true - вказує, що сервер буде запущено при старті системи
```
- name: Enable a timer unit for dnf-automatic
  ansible.builtin.systemd_service:
    name: containerd
    state: started
    enabled: true
  become: yes
```
# Включити інші таски з іншого файлу
тот є кілька цікавостей, по перше ця команда виконується при виконанні скрипту і фактично з додаванням when, можна пропустити додавання цих тасків
```
- name: Include Kubernetis
  include_tasks: kubernetis.yaml
```
(include_tasks)[https://docs.ansible.com/ansible/2.9/modules/include_module.html]

# Встановлення граничного часу виконання команди
Для команди можна задати timeout якій вкаже скільки чекати до завершення команди поки команда не буде визнана такою що повалилася.
(є глобальне значення а це значення для конкретної команди)
```
- name: create master node
  ansible.builtin.shell: "kubeadm init --control-plane-endpoint={{ ansible_hostname }}.bs.local.erc --ignore-preflight-errors=Mem --pod-network-cidr={{ kuber_net }}"
  timeout: 600
  register: kubectlconfig
```

# Отримання інформації про користувача
## через ansible_facts
```
- name: debug
  debug:
    msg: "{{ ansible_facts.user_id }}: {{ ansible_facts.user_uid }}:{{ ansible_facts.user_gid }}"
```
## через getent
```
- getent:
  database: passwd
- name: debug
  debug:
    msg: "{{ ansible_user }}: {{ getent_passwd[ansible_user].1 }}:{{ getent_passwd[ansible_user].2 }}"
```
## через виконання команд
```
- name: Execute id command
  command: id -u {{ ansible_user }}
  register: ansible_user_uid

- name: Debug Ansible user UID
  debug:
    var: ansible_user_uid.stdout

- name: Execute id command
  command: id -g {{ ansible_user }}
  register: ansible_user_gid

- name: Debug Ansible user primary GID
  debug:
    var: ansible_user_gid.stdout
```
[https://www.laurivan.com/uid-and-gid-of-default-ansible-user/]
