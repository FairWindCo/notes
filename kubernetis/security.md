# За мотивами курсу Certified Kubernetes Security Specialist (CKS)

## Початкові роботи по налаштуванню кластеру:
### Встановлення докер
`curl https://releases.rancher.com/install-docker/20.10.sh | sh `

### Встановлення куберу
```
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/kubernetes=xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

`sudo apt-get update`
Саме встановлення
`sudo apt-get install -y kubelet kubeadm kubectl`
Блокування кубернетіса від зміни 
`sudo apt-mark hold kubelet kubeadm kubectl`

Рекомендація 
створити файл /etc/docker/daemon.json зі зімстом:
```
{
"exec-opts": ["native.cgroupdriver=systemd"]
}
```
та перезавантажети демона
```
systemctl deamon-reload
systemctl restart docker
systemctl restart kubelet.service
```


`kubeadm init --apiserver-advertise-address=<master-node-ip> --pod-network-cidr=<pod-network>`
наприклад:
`kubeadm init --apiserver-advertise-address=95.217.134.250 --pod-network-cidr=172.16.0.0/16`

якщо вже була спроба встановити то можливо воникниння помилки типу
/var/lib/etcd is not empty

в такому разі зміюємо команду для ігнорування попереджень:
`kubeadm init --apiserver-advertise-address=<master-node-ip> --pod-network-cidr=<pod-network> --ignore-preflight-errors=all`
приклад:
`kubeadm init --apiserver-advertise-address=95.217.134.250 --pod-network-cidr=172.16.0.0/16  --ignore-preflight-errors=all`


Після завершення встанвовлення бачимо код, що потрібно виконати, це щось типу такого:
це код ствоерння конфігу для kubectl
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Для користувача root:
`export KUBECONFIG=/etc/kubernetes/admin.conf`


для підключення інших робочіх нод використувуємо код що має такий вигляд:
`kubeadm join <master-node-ip> --token <token> --discovery-token-ca-cert-hash sha256:<hash>`
значення хещів та токенів зразу можна побачити після завершення розгортання головної ноди (прямо в виводі команди розгортання) або окремо запитувати про них кластер


Проте якщо зразу перевірити кластер то маємо такий стан:
`kubectl get nodes`
```
NAME    STATUS     ROLES
master  NotReady   control-plane,master
worker  NotReady   <none>
```
Всі ноди в стані не готово бо не встановлена система мережі CNI кластеру її треба встановлювати коремо.

Install calico:
```
curl https://docs.projectcalico.org/manifests/calico.yaml -O
kubectl apply -f calico.yaml
```
після цього виконуємо команду
`watch -n 1 kubectl get nodes`
та дивимось як ноди переходять в стан Ready 

КЛАСТЕР ВСТАОВЛЕНО


## МЕРЕЖЕВІ ПОЛІТИКИ В КЛАСТЕРІ
це набори правил (як правила фаєрволу, що регулують поведінку трафіку в середині  кластеру та зовні по відношенню до нього.
Ці набори правил реалізують системи такі як calico, weave, flannel....

Можна обмедити Ingress\Egress  трафік для групи подів базуючись на правилах та умовах.
- Ingress - вхідний трафік до подів
- Egress - вихідний трафік

По замовченню дозволено все і всі поди бачать один одного.

Команда створення пода (для тесту):
`kubectl run pod-1 --image=nginx`
Маємо вивід, щось на зразок:
pod/pod-1 created
Файктично команда запускає образ всередені кластеру та дає йому ім'я "pod-1"

Можна відкрити порт
`kubectl expose pod <ім'я пода> --port <номер порту>`
Наприклад:
`kubectl expose pod pod-1 --port 80`

Подивитися доступні сервіси можна командою
`kubectl get svc`


Перевірити роботу тестового серверу можна підключившись до консолі ноди кластеру:
`kubectl exec <pod> -it -- bash`
а в консолі наприклад можна визвати curl pod-1, що зможе підключитися до поду та вивисти тестову сторінку
Або безпосередньо виконати команду на поді:
`kubectl exec <pod> -- curl <тестове посилання>`
наприклад:
`kubectl exec pod-1 -- curl pod-2`


створюжмо політику мережі:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: test-network-police
    namespace: default
spec:
    podSelector: {}
    policeTypes:
    - Ingress
    - Egress
```

`kubectl apply -f <файл з політикою>`
Такий файл політики забороняє весь трафік між подами кластеру.
Це така собі зоборона всього за замовченням.

Перегляд політик:
`kubectl get NetworkPolicy`


Проста політика, що дозволяє трафак від одного поду до іншого:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: egress-pod-1
    namespace: default
spec:
    podSelector:
      matchLabels:
        run: pod-1
    policeTypes:
    - Egress
    egress:
    - to:
      - podSelector:
          matchLabels:
            run: pod-2
```
Таке правило дозволяє зовіншній трафік від пода поміченого міткою pod-1 до поду помічкенного міткою pod-2. Проте це відкриє лише шлях від поду-1, але немає дозволу на прийом для поду-2. Для того, щоб відкрити треба створити ще одну політику:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: ingress-pod-2
    namespace: default
spec:
    podSelector:
      matchLabels:
        run: pod-2
    policeTypes:
    - Ingress
    ingress:
    - from:
      - podSelector:
          matchLabels:
            run: pod-1 
```
Проте політика за замовченням (блокувати все, блокує також і ДНС, тому поди не будуть резолвити)
Політика дозволів для DNS
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: dns
    namespace: default
spec:
    podSelector: {}
    policeTypes:
    - Egress
    egress:
    - ports:
      - port: 53
        protocol: UDP
      - port: 53
        protocol: TCP
```
ця частина "    podSelector: {}" вказує на всі поди

Ще одна замітка по прикладу, що наведені два правила дозволять трафік лише з под1 на под2, проте запити в зворотньому боці працювати не будуть. Тобто:
`kubectl exec pod-1 -- curl pod-2`
спрацює, проте команда:
`kubectl exec pod-2 -- curl pod-1`
вде не спрацює, бо дозволено лише надсилати трафік від под1 та приймати трафік на под2



Для теста створюємо окремий простір імен з ще одним подом там:
```
kubectl create ns prod
kubectl run pod-3 --image=nginx -n prod
kubectl expose pod pod-3 --port=80 -n prod
```
Після чого редагуємо простір імен
`kubectl edit ns prod`
Тут попадаємо в редактор, та додаємо в розділ metadata\labels значення "ns:prod", те саме робимо і з простором за зомовчуванням:
`kubectl edit ns default`
(після виходу з редактору зміни приміняються автоматично)

Для зміни тестового прикладу, щоб под2 мав також змогу спілкуватися з подом3 в іншому просторі, змінимо його політику так:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: ingress-pod-2
    namespace: default
spec:
    podSelector:
      matchLabels:
        run: pod-2
    policeTypes:
    - Ingress
    - Egress
    ingress:
    - from:
      - podSelector:
          matchLabels:
            run: pod-1 
    egress:
    - to:
      - namespaceSelector:
          matchLabels:
            ns: prod
```

Проте тут варто зазначити, кілька моментів:
- поди з простору імен за замовчуванням не знають про інсування подів в іншому просторі, тому доступ по імені не можливий лише за ІР.
- так як політика блокувати все діє лише на простір за замовченням, то в просторі прод, дозволено будь який трафік, тому для доступа з под2 достатньо створити лише вихідне правило для трафіку і все запрацює, але лише за ІР адресою.

Тому простір прод, потребує політику блокування:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: test-network-police
    namespace: prod
spec:
    podSelector: {}
    policeTypes:
    - Ingress
    - Egress
```

Але після її застосуваня доступ з под2 на под3 буде заборонено, треба створити вхідну політику:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: ingress-pod-2
    namespace: prod
spec:
    podSelector:
      matchLabels:
        run: pod-3
    policeTypes:
    - Ingress
    ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            ns: default
```
-------------------------------------------------------------------------------
## ВСТАНОВЛЕННЯ dashboard

за адресою https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/

беремо стоку встановлення та застосовуємо:
`kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml`


після чього перевіряємо, що все працює:
`kubectl get all -n kubernetes-dashboard`

тут бачимо деяку кулькість різних об'єктів, сервіси, поди, репліки и т.п.

Для того, щоб коректно працювати вносимо зміни в деплой:

`kubectl edit deploy kubernetes-dashboard -n kubernetes-dashboard`

пропонується в розділі:
```
containers:
 - args:
   - --auto-generate-certificates
   - --namespace=kubernetes-dashboard
```
замінити "   - --auto-generate-certificates" на "   - --insecure-port=9090"
та в розділі
livenessProbe 
змінити scheme: HTTPS на scheme: HTTP, та порт на 9090
Або прибрати пробу взагалі

Також необхідно змінити сервіс

`kubectl edit service\kubernetes-dashboard -n kubernetes-dashboard`

та змінити там порт з 8443 на 9090, та з 443 на 9090, повинно стати type: nodePort (замість балансування)

Далі в переліку сервісів дивимося:
`kubectl get service  -n kubernetes-dashboard`
ми повінні бачити щось на зразок
```
NAME                           TYPE        CLUSTER-IP        EXTERNL-IP   PORTS(s)
.......
service/kubernetes-dashboard  NodePort    xxx.xxx.xxx.xxx    <none>       9090:<число>/TCP
```
ось це число, це й буде номер порту за яким на нодах буде органызовано прослуховування.

Підключитсия до сервісу буде можна по <ІР адреса ноди>:ПОРТ_прослуховування


Проте є проблеми з доступом до функцій, ми нічого не бачимо в середині дашборду. 
для їх виправлення

`kubectl get sa -n kubernetes-dashboard`
тут бачимо назву сервісного акаунту в дашборді

а ця команда показує ролі для перегляду елементів кластеру
`kubectl get clusterroles | grep view`

Тепер треба створити прив'язування ролі до сервісного акаунту:
`kubectl create rolebinding insecure --serviceaccount kubernetes-dashboard:kubernetes-dashboard --clusterrole view -n kubernetes-dashboard`
(це даэ права бачити лише об'єкти з простору kubernetes-dashboard, інші будуть не доступні в тому числі й той, що за замовчанням)

Даємо право на весь кластер:
`kubectl create clusterrolebinding insecure --serviceaccount kubernetes-dashboard:kubernetes-dashboard --clusterrole view -n kubernetes-dashboard`


## Ingress Controller
https://github.com/kubernetes/ingress-nginx/blob/main/docs/deploy/baremetal.md
https://github.com/kubernetes/ingress-nginx


install instruction:
`https://kubernetes.github.io/ingress-nginx/deploy/`


install
`kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml`

або через HELM
```
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```
Перелік доступних версій:
`helm show values ingress-nginx --repo https://kubernetes.github.io/ingress-nginx`

Після встановлення, перевіряємо робочі елементи:
`kubectl get all -n ingress-nginx`

тут ми бачимо сервіси, та можемо визначити номер порту ноди який прослуховується сервісом. Тож маємо змогу підключитися до нього і побачити відповідь nginx

Тепер звідси беремо мінімальний опис:
https://kubernetes.io/docs/concepts/services-networking/ingress/

Він має такий вигляд:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx-example
  rules:
  - http:
      paths:
      - path: /testpath
        pathType: Prefix
        backend:
          service:
            name: test
            port:
              number: 80
```

Тут важливо, щоб був сервіс з іменем test, який можна например створити:

варіант на основе nginx
`kubectl run pod-1 --image=nginx`
`kubectl expose pod pod-1 --port=80 --name test1`

варіант на основі apache
`kubectl run pod-2 --image=httpd`
`kubectl expose pod pod-2 --port=80 --name test2`

та тестовий контроллер:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx-example
  rules:
  - http:
      paths:
      - path: /testpath1
        pathType: Prefix
        backend:
          service:
            name: test1
            port:
              number: 80
      - path: /testpath2
        pathType: Prefix
        backend:
          service:
            name: test2
            port:
              number: 80
```

Наступна проблема, полягає  втому, що інгрес контроллер має крім HTTP ще й HTTPS порт, проте на цьому порті за хамовчуванням встановлено фейковий сертифікат.

Для того, щоб встановити свій треба його згенерувати:
`openssl req -x509 -newkey rsa:4096 -keyout key.pem out cert.pem -days 365 -nodes`

Додаємо сертифікат в якості секрета кубернетіса:
`kubectl create secret tks secure-ingress --cert=cert.pem --key=key.pem`

Після чого вносимо зміни в наш тестовий контроллер:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  tls:
  - hosts:
      - https-example.foo.com
    secretName: secure-ingress
  rules:
  - host: https-example.foo.com
  - http:
      paths:
      - path: /testpath1
        pathType: Prefix
        backend:
          service:
            name: test1
            port:
              number: 80
      - path: /testpath2
        pathType: Prefix
        backend:
          service:
            name: test2
            port:
              number: 80
```
Та застосовуємо його.

Перевіряємо:
`curl https://<node_ip>:<node_port_ingress_https>/testpath1 -kv`




## Заборонити доступ з конкретного хосту
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: deny
    namespace: default
spec:
    podSelector: {}
    policeTypes:
    - Egress
    egress:
    - to:    
      - ipBlock:
          cidr: 0.0.0.0/0
          except:
            - 169.254.169.254/32
```
Це правило забороняє трафік до  хосту 169.254.169.254/32


## ПЕРЕВІРКА КЛАСТЕРУ НА БЕЗПЕКУ
є тест на зразок kube-bench, що виконують перевірку стану кластеру згідно з певними рекомендаціями https://www.cisecurity.org/benchmark/kubernetes/
Репозиторій доступний тут:
https://aquasecurity.github.io/kube-bench/v0.6.15/


Встановлення:
`curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_amd64.deb -o kube-bench_0.6.2_linux_amd64.deb`

`sudo apt install ./kube-bench_0.6.2_linux_amd64.deb -f`

Запуск через команду:
`kube-bench`


Як алтернатива можна скачати бінарніки самостійно
```
curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_amd64.tar.gz -o kube-bench_0.6.2_linux_amd64.tar.gz
tar -xvf kube-bench_0.6.2_linux_amd64.tar.gz
```
але тоді при запуску треба вказувати шлях до конфігу, наприклад так:

`./kube-bench --config-dir `pwd`/cfg --config `pwd`/cfg/config.yaml `


Проте гарний варіант запуск як таску для кубера, для цього качаємо файл
https://github.com/aquasecurity/kube-bench/blob/main/job.yaml

`wget https://github.com/aquasecurity/kube-bench/blob/main/job.yaml`
та застосовуємо його:
`kubectl apply -f job.yaml`

Перевіряємо, що створився под kube-bench-ххххх, і чекаємо поки він перейде в статус complete
Перевірка `kubectl get pods`
Далі дивимося його логи:
`kubectl logs kube-bench-ххххх`


## ПЕРЕВІРКА БІНАРННИХ ФАЙЛІВ КЛАСТЕРУ

Заходимо за силкою на реліз:
https://github.com/kubernetes/kubernetes/releases/tag/v1.28.3
(остання частина номер версії)
переходимо за посиланням CHANGELOG та шукаємо там Server Binaries

наприклад качаємо там kubernetes-server
https://dl.k8s.io/v1.28.3/kubernetes-server-linux-amd64.tar.gz
і перевіряємо
`sha512sum kubernetes-server-linux-amd64.tar.gz`
порівнюємо результат з значенням на сайті

Розпаковуємо:
```
tar zxf kubernetes-server-linux-amd64.tar.gz
cd kubernetes/server/bin
```

`sha512sum kube-apiserver`
отримаємо еталоний хешкод


Далі дивимося потрібний нам контейнер:
`docker ps | grep kube-apiserver`
знаходимо ID контейнера xxxxxxx
та копіюємо його вміст в папку container
`docker cp xxxxxxx:/ container`
шукаємо файл 
`find container/ | grep kube-apiserver`

`sha512sum container/usr/local/bin/kube-apiserver`

та порівнюємо хеші



## RBAC (Role Based Access Control)
Дозволяє обмежити доступ до ресурсів кластеру для користувачів або сервісних акаунтів

В кастері є два типи ресурсів:
 - ті що можуть бути в просторі імен (Namespaced)
   можна побачити командою 
   `kubectl api-resources --namespaced=true`
 - ті що незалежать від простору імен (Non Namespaced)
   можна побачити командою 
   `kubectl api-resources --namespaced=false`

Наприклад:
```
Namespaced (role)			Non Namespaced (cluster role)
-------------------------------------------------
pods (po)                        nodes    (no)
services (svc)                   namespaces  (ns)
secrets                           
persistentvolumeclaim (pvc)      persistentvolumes (pv)
roles                            clusterroles
......				 ......
```

 Можна задавати набори прав
 - може редагувати поди (can edit pods)
 - може читати сикрети (can read the secrets)

Тоді ці права можна зв'язти через RoleBinding та ClusterRoleBinding, які задають хто отримає ці права (роль чи кластерна роль).
 
ClusterRole\ClusterRoleBinding - застосовуються для всіх існуючих чи майбуніх просторів імен.
Role\RoleBinding - застосовуються для всіх існуючих чи майбуніх ресурсів у вказаному просторі імен.

## Створення ролі
Роль, що буде створена в просторі імен prod буде називатися secret-manager, буде давати право виконувати операцію get на ресурсі secret:
В другому прикладі бачимо можливість задати одразму кілька дозволених операцій.
```
kubectl -n prod create role secret-manager --verb=get --resource=secret
kubectl -n prod create role secret-manager2 --verb=get --verb=list --resource=secret
```
Після чого треба прив'язати (RoleBinding) роль до користувача, зв'язуючи користувача test з роллю secret-manager:
```
kubectl -n prod create rolebinding secret-manager-bind --role=secret-manager --user=test
```


Розглянемо тестовий приклад:
Ствоермо два простори імен prod та deploy
- користувач test може лише дивитися секрет в просторі prod
- користувач test може лише дивитися секрет та переглядати перелік секретів в просторі deploy
- також перевіремо чи може користувач test виконувати відповідні дії (can-i)
```
kubectl create ns prod
kubectl create ns deploy
```
В просторі prod  створюємо роль менеджер секретів
`kubectl -n prod create role secret-manager --verb=get --resource=secrets`

даємо цій ролі можливість виконувати команду get для ресупсів secrets

Створюємо прив'язування ролі до користувача:
`kubectl -n prod create rolebinding secret-manager --role=secret-manager --user=test`

Тут створюється зв'зування з іменем secret-manager, де роль secret-manager прив'язується до користувача test

В іншому просторі робимо аналогічну роль
`kubectl -n deploy create role secret-manager --verb=get --verb=list --resource=secrets`

та прив'язуємо роль до користувача тільки вже в цьому просторі імен
`kubectl -n deploy create rolebinding secret-manager --role=secret-manager --user=test`

## Тестування прав
Існіє спеціальна команда яка каже чи може користувач виконати певні дії з певними об'єктами

Чи можу я виконати дії у відповідних просторах:
```
kubectl auth can-i get secrets -n prod
kubectl auth can-i get secrets -n deploy
kubectl auth can-i list secrets -n prod
kubectl auth can-i list secrets -n deploy
```
Чи може користувач тест виконати вибрані дії у відповідних просторах:
```
kubectl auth can-i get secrets -n prod --as test
kubectl auth can-i get secrets -n deploy --as test
kubectl auth can-i list secrets -n prod --as test
kubectl auth can-i list secrets -n deploy --as test
```
Для перевірки своїх прав доступу ісує спеціальна команда:
Перший варіант перевіряє чи можу я створювати поди у всіх просторах імен
Другий варіант перевіряє чи може користувач test-user я бачити всі поді в протсорі імен test
Третій варіант перевіряє чи можу я робити, що завгодно з чим завгодно в поточному просторі імен
Четвертий варіант показує всі дозволені дії в просторі імен test
```
kubectl auth can-i create pods --all-namespaces
kubectl auth can-i list pods -n test --as test-user
kubectl auth can-i '*' '*'
kubectl auth can-i --list --namespace=test
```
Інші корисні перевірки:
Перевірка що я можу робити все, що завгодно з усіма обє'ктами в протсорі default
`kubectl auth can-i '*' '*'`

Перевірка що я можу робити все, що завгодно з секретами в протсорі default
`kubectl auth can-i '*' secrets`

Перевірка що я можу робити все, що завгодно з усіма обє'ктами в протсорі <name-space>
`kubectl auth can-i '*' '*' -n <name-space>`

Перевірка що я можу робити все, що завгодно з секретами в протсорі <name-space>
`kubectl auth can-i '*' secrets -n <name-space>`

Переглад всіх дозволів для вказаного простору <name-space>
`kubectl auth can-i --list -n <name-space>`


Розглянемо другий варіант, надамо корисувачу test право видаляти деплойменти у всіх простарах імен
А користувачу new видяляти деплоймент лише в просторі danger
```
kubectl create clusterrole undeployment-role --verb=delete --resource=deployment
kubectl create clusterrolebinding undeployment-role-test --clusterrole=undeployment-role --user=test

kubectl create ns danger
kubectl -n danger create rolebinding undeployment-role-test --clusterrole=undeployment-role --user=new


kubectl auth can-i delete deployment --as test
kubectl auth can-i delete deployment --as test -n prod
kubectl auth can-i delete deployment --as test -n deploy
kubectl auth can-i delete deployment --as test -n danger
```

і всюди буде відповідь yes
`kubectl auth can-i delete deployment --as new -n danger`

тут беде відповідь yes, а для інших запитів:
```
kubectl auth can-i delete deployment --as new
kubectl auth can-i delete deployment --as new -n prod
kubectl auth can-i delete deployment --as new -n deploy
```
відповідь буде no


## Акаунти
в кластері існує два типи акаунтів
- сервісні акаунти,  найчастіше вокористовується машинами, такими як поди, для авторизації доступу до АРІ та зовнішніх сервісів. Самі такі севісні акаунти створюються, змінюються і видаляються через АРІ кубера;
- та нормальні акаунти користувачів. (кожен з яких має свій секртифікат та ключ видані СА certificate authority кластера кубера, обов'язково сертифікат повинен мати CN (common name) в іменем користувача. За допомогою цих даних, можна виконувати команди в АРІ згідно з визначеними ролями.

Для організації доуступу користувача створюємо ключ:
`openssl genrsa -out intern.key 2048`

він буде в файлі intern.key

Далі створюємо CSR (Certificate Signing Request) — це ключ, який генерується при запиті на видачу сертифіката.

`openssl req -new -key intern.key -out inter.csr`

Майже всі поля заповнюємо за своїм роззудом, єдине, що важливо це значення яке ми запишемо в CN (common name).
В нашому прикладі ми назвемо кристувача intern

Маємо два файли: inter.csr та intern.key
Далі дивимося в документації:
[https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#create-certificatessigningrequest]

Переводимо вміст файлу inter.csr в base64, це можна зробити командою:
`cat intern.csr | base64 -w 0`

Створюємо файл csr.yaml:
```
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: <ім'я користувача вказане в CN сертифікату>
spec:
  request: <вміст файлу csr  в форматі base64 взяте на попередньому кроці>
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: 86400  # це значення видалити, або встановити на потрыбний час
  usages:
  - client auth
```

Файл матиме вигляд на зразок такого:
```
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: intern
spec:
  request: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0KTUlJQ1ZqQ0NBVDRDQVFBd0VURVBNQTBHQTFVRUF3d0dZVzVuWld4aE1JSUJJakFOQmdrcWhraUc5dzBCQVFFRgpBQU9DQVE4QU1JSUJDZ0tDQVFFQTByczhJTHRHdTYxakx2dHhWTTJSVlRWMDNHWlJTWWw0dWluVWo4RElaWjBOCnR2MUZtRVFSd3VoaUZsOFEzcWl0Qm0wMUFSMkNJVXBGd2ZzSjZ4MXF3ckJzVkhZbGlBNVhwRVpZM3ExcGswSDQKM3Z3aGJlK1o2MVNrVHF5SVBYUUwrTWM5T1Nsbm0xb0R2N0NtSkZNMUlMRVI3QTVGZnZKOEdFRjJ6dHBoaUlFMwpub1dtdHNZb3JuT2wzc2lHQ2ZGZzR4Zmd4eW8ybmlneFNVekl1bXNnVm9PM2ttT0x1RVF6cXpkakJ3TFJXbWlECklmMXBMWnoyalVnald4UkhCM1gyWnVVV1d1T09PZnpXM01LaE8ybHEvZi9DdS8wYk83c0x0MCt3U2ZMSU91TFcKcW90blZtRmxMMytqTy82WDNDKzBERHk5aUtwbXJjVDBnWGZLemE1dHJRSURBUUFCb0FBd0RRWUpLb1pJaHZjTgpBUUVMQlFBRGdnRUJBR05WdmVIOGR4ZzNvK21VeVRkbmFjVmQ1N24zSkExdnZEU1JWREkyQTZ1eXN3ZFp1L1BVCkkwZXpZWFV0RVNnSk1IRmQycVVNMjNuNVJsSXJ3R0xuUXFISUh5VStWWHhsdnZsRnpNOVpEWllSTmU3QlJvYXgKQVlEdUI5STZXT3FYbkFvczFqRmxNUG5NbFpqdU5kSGxpT1BjTU1oNndLaTZzZFhpVStHYTJ2RUVLY01jSVUyRgpvU2djUWdMYTk0aEpacGk3ZnNMdm1OQUxoT045UHdNMGM1dVJVejV4T0dGMUtCbWRSeEgvbUNOS2JKYjFRQm1HCkkwYitEUEdaTktXTU0xMzhIQXdoV0tkNjVoVHdYOWl4V3ZHMkh4TG1WQzg0L1BHT0tWQW9FNkpsYWFHdTlQVmkKdjlOSjVaZlZrcXdCd0hKbzZXdk9xVlA3SVFjZmg3d0drWm89Ci0tLS0tRU5EIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLQo=
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: 86400  # one day
  usages:
  - client auth
```
Застосовуємо його
`kubectl apply -f csr.yaml`

отримаємо відповідь:
`certificatesigningrequest.certificates.k8s.io/myuser created`


Далі дивимося запити:
```
kubectl get csr


NAME      AGE   SIGNERNAME                                    REQUESTOR              CONDITION
csr-kt8pj 47m kubernetes.io/kube-apiserver-client-kubelet system:bootstrap:24taq4 Approved,Issued
intern    10s kubernetes.io/kube-apiserver-client         kubernetes-admin        Pending
```

Бачимо, що intern в статусі Pending
Важливо розуміти, що в нашому випадку правильним іменем користувача має бути intern, бо це ім'я вказане при створенні запиту на сертифікат. В разі якщо, запит треба видалити, можна використати команду:
`kubectl delete csr <ім'я користувача>`

А для отриманання доступу запит треба підтвердити, це можна зробити командою:
`kubectl certificate approve <ім'я користувача>`

В нашому випадку це:
`kubectl certificate approve intern`

Після чого перевіряємо:
```
kubectl get csr

NAME      AGE   SIGNERNAME                                    REQUESTOR              CONDITION
csr-kt8pj 47m kubernetes.io/kube-apiserver-client-kubelet system:bootstrap:24taq4 Approved,Issued
intern    10s kubernetes.io/kube-apiserver-client         kubernetes-admin        Approved,Issued
```

Маємо статус Approved,Issued - все добре

Тепер треба дістати сам сертифікат:
`kubectl get csr <ім'я користувача> -o yaml`

Наприклад:
`kubectl get csr intern -o yaml`


тут ми побачимо значення 
certificate: <код в base64> 

це і буде значення сертифікату
його треба перетворити на файл сертифікату, для цього копіюємо значення та вставляємо в команду:
`echo <код в base64> | base64 -d >inter.crt`

отримаємо файл intern.crt з сертифікатом

Дивимося файл конфігурації кубернетіс
```
kubectl config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://<сервер>:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: DATA+OMITTED
    client-key-data: DATA+OMITTED
```
Треба додати в конфігурацію новий ключ:

`kubectl config set-credentials intern --client-key=intern.key --client-certificate==intern.crt --embed-certs`

Тепер при виконанні команди:
`kubectl config view`

ми побачимо вже і нашого користувача

Тепео плтрібно створити контекст:
```
kubectl config set-context intern --user=intern --cluster=kubernetes

kubectl config view
```
ми побачимо вже і нашого користувача і новий контекст

крім того наявні контексти можна побачити командою:
`kubectl config get-contexts`

Перемикання контексту командою
`kubectl config use-context <ім'я контексту>`

в нашому випадку
`kubectl config use-context intern`

Сервісни акаунти
---------------------------------------------------------------------------------------------------
Сервісни акаунти, вони завжди відносяться до якогось простору імен (за замовченням це default).
Під кожний SA (сервіс акаунт) створюється сикрет який зберігає АРІ ключ, та який може бути використаний для взіємодії з сервісами кубернетіс.

Подивитися ісуючи сервісни аканути та їх ключи можна за домопогою команди:
`kubectl get sa,secrets`

Наприклад маємо такий результат:
```
kubectl get sa,secrets
NAME                     SECRETS   AGE
serviceaccount/default   0         91d

NAME                                             TYPE                DATA   AGE
secret/haproxy-kubernetes-ingress-default-cert   kubernetes.io/tls   2      89d
```
Подивитися, що всередині ключа
`kubectl describe secret <назва_ключа>`

і там можна побачити токен

можна створити власний сервісний акаунт:
`kubectl create sa <ім'я акаунту>`

Приклад:
`kubectl create sa test`

Тут ціково, бо за інформацією автоматично повинен бути створений і сикрет, що зберігає токен.
Проте в випадку версії 1.28 цього автоматично не стається.

Для створення токену слугує команда:
`kubectl create token <сервісний акаунт>`

Наприклад:
`kubectl create token test`

Версії Kubernetes до версії 1.22 автоматично створювали довгострокові облікові дані для доступу до API Kubernetes. Цей старіший механізм базувався на створенні маркерів Secrets, які потім можна було монтувати в запущені модулі. У новіших версіях, включаючи Kubernetes v1.29, облікові дані API отримують безпосередньо за допомогою API TokenRequest і монтуються в Pods за допомогою проектованого тому. Токени, отримані за допомогою цього методу, мають обмежений час життя та автоматично стають недійсними, коли видаляється Pod, до якого вони монтуються.

Проте є можливість явно ствоити такий токен, за страим зарзком для цього застосовуємо деплоймент типу такого, де build-robot, це ім'я сервісного акаунту
```
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: build-robot-secret
  annotations:
    kubernetes.io/service-account.name: build-robot
type: kubernetes.io/service-account-token
EOF
```

Перевірити такий сикрет можна:
```
kubectl get secret/build-robot-secret -o yaml
```
А подивитись токен, командою:
```
kubectl describe secrets/build-robot-secret
```
Сам по собі сервісний акаунт можна використати наступним чином:
1. Створюємо деплоймент, командою
`kubectl run test --image=nginx --dry-run=client -o yaml`

яка на виході дає наступний вивід, що можна зберігти в файл:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test
  name: test
spec:
  containers:
  - image: nginx
    name: test
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
Додаємо опис сервісного акаунту в специфікацію:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test
  name: test
spec:
  serviceAccount: test
  containers:
  - image: nginx
    name: test
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

тоді якщо застосувати:
`kubectl apply -f `

Якщо тепер підключитися в консоль поду, командою на зразок такої (де test - це ім'я пода):
`kubectl exec -it test bash`

в середині контейнера можливо побачити підмаунчену файлову систему: `mount | grep sec`
```
tmpfs on /run/secrets/kubernetis.io/serviceaccount type tmpfs (ro,relatime)
```
за цим шляхом "/run/secrets/kubernetis.io/serviceaccount" буде знаходитись сертифікат та токен доступу.
Ці дані дозволяють отримувати доступ до АРІ кластеру, якщо всередині контейнеру виконати команду:
`curl https://kubernetes -k`

то отримаємо json відповідь де буде сказано, що анонімний користувач не має дуступу до АРІ кластеру (це тому, що був анонімний доступ).

Для того, щоб мати авторизований доступ, потрібно взяти зміст файлу token з каталогу /run/secrets/kubernetis.io/serviceaccount та вставити його в команду:
`curl https://kubernetes -k -H "Authorization: Bearer token_data"`

в цьоу випадку система поверне відповідь, що доступу немає в сервісного акаунту з нашого простору імен. Далі потрібно налаштувати відповідний дсотуп для самого акаунту.

Проте, часто не потрібно, щоб сервісний акаунт був постійно підключений до контейнеру, для цього слугує опція "automountServiceAccountToken: false", якщо змінити деплоймент наступним чином, то побачемо, що сервійний акаунт не буде замаунчений в середені контейнера. 
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test
  name: test
spec:
  serviceAccount: test
  automountServiceAccountToken: false
  containers:
  - image: nginx
    name: test
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
Обмеження сервісних акаунтів за допомогою RBAC
-------------------------------------------------

По замовчуванню сервісний акаунт немає жодних прав.
Перевирити це можна командою:

`kubectl auth can-i delete secret --as system:serviceaccount:default:test`

де default - це простір імен в якому розміщено сервісний акаунт, а test - це сервісний акаунт від імені якого йде первірка
ця команда перевірить чи може сервісний акаунт test з простору імен default видаляти секрети.

`kubectl create clusterrolebinding test-binding --clusterrole edit --serviceaccount default:test	`

Ця команда призначить сервісному акаунту test з простору імен default - кластерну роль edit
(перелік доступних ролей можна подивитися `kubectl get clusterrole`)



Блокування\Розблокування анонімного доступу до кластеру
--------------------------------------------------------
Дивлячись на файл /etc/kubernetes/manifests/kube-apiserver.yaml
можна побачити в розділі command аргументи запуску сервісу.
```
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubeadm.kubernetes.io/kube-apiserver.advertise-address.endpoint: 10.225.24.26:6443
  creationTimestamp: null
  labels:
    component: kube-apiserver
    tier: control-plane
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
    - --advertise-address=10.225.24.26
    - --allow-privileged=true
    - --authorization-mode=Node,RBAC
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --enable-admission-plugins=NodeRestriction
    - --enable-bootstrap-token-auth=true
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
    - --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key
    - --etcd-servers=https://127.0.0.1:2379
.......
```

Тут є аргумент --authorization-mode=Node,RBAC
(параметри можуть бути й іншими)
За замовчуванням якщо спробувати отримати доступ до АРІ кластеру то отримаємо помилку заборони анонімного доступу:
`curl https://localhost:6443 -k`

поверне json об'єкт:
```
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "forbidden: User \"system:anonymous\" cannot get path \"/\"",
  "reason": "Forbidden",
  "details": {},
  "code": 403
}
```
Де прямо сказано, що system:anonymous - намає доступу до АРІ.

Якщо додати до команного рядка аргумент --anonymous-auth=false, то можна керувати доступом від анонімного користувача
```
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubeadm.kubernetes.io/kube-apiserver.advertise-address.endpoint: 10.225.24.26:6443
  creationTimestamp: null
  labels:
    component: kube-apiserver
    tier: control-plane
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
    - --anonymous-auth=false
    - --advertise-address=10.225.24.26
    - --allow-privileged=true
    - --authorization-mode=Node,RBAC
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --enable-admission-plugins=NodeRestriction
    - --enable-bootstrap-token-auth=true
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
    - --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key
    - --etcd-servers=https://127.0.0.1:2379
.....
```
Причому нічого не треба перезавантажувати а лише зачекати кілька хвилин. Тоді помилка зміниться на значення не авторизовано. Тобто анонімний користувач просто не взагалі не отримає доступ до АРІ кластеру.
Перевіряємо: `curl https://localhost:6443 -k`
Отримаємо відповідь.
```
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "Unauthorized",
  "reason": "Unauthorized",
  "code": 401
}
```
Проте значення --anonymous-auth=true, навпаки відкриває анонімний доступ до АРІ. Проте користувачу anonymous не надано прав, тому в цьому випадку йому просто буде заборонено доступ до функцій АРІ, але підключення до серверу буде дозволено.

# Ручний доступ до API
Переглянемо конфігурацію кластеру:
`kubectl config view`

ця команда видасть, щось на зразок цього:
```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://kuber0101.bs.local.erc:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: DATA+OMITTED
    client-key-data: DATA+OMITTED
```
Проте в цьому виводі замінені сертифікати, їх можна побачити вказавши параметр
`kubectl config view --raw` - в цьому випадку ми будемо бачити закодовані в base64 сертифікати, наприклад:
```
kubectl config view --raw
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURCVENDQWUyZ0F3SUJBZ0lJSTc1RG8yczVVR3d3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TXpBNU1UZ3dOakEwTWpGYUZ3MHpNekE1TVRVd05qQTVNakZhTUJVeApFekFSQmdOVkJBTVRDbXQxWW1WeWJtVjBaWE13Z2dFaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQkR3QXdnZ0VLCkFvSUJBUUNxekZiSzFWUFNrUmNaOUxQVmRsWEp2MHBVTlBCV0h1UnhiRjA3alpSQWNScFFMUGdkOGpabmthVEYKc1hRbUV2aXltU1psbnNGRmwwWmZIRThqRktReFNySTNUaHZTM0o3cVIyOWpZOC9WNFBEMkhEYTVpdXhzRWFZbgpwbjZ4QWt0akVNNXd6Tmd6eDlsSkEzb2xWckNWQkNXdk1ET1Z5VmQ4ZVpPbUFIY0FoZTBqcTVyQzNVaFJLVjdvCkZ2Q1NkKzlNUU51cHJEM2Q4OEhaSGJsZFVUeGxEZGUvVTFXenRYbGVLUkt6MzFhUXNKQU4vb1RtOFRyQi9yeHQKRkdWbmQxYW1rbEFNb2ttdTZaSmtyRjRMVE56RzMwMngrRmtTZ0NDdU1lTHpJa0tYVXFiWklKU2JKbkNJOHkwYQpqL1M1TUxPK3FVTzdLb2laN1AxTU9Ca2lBc0FOQWdNQkFBR2pXVEJYTUE0R0ExVWREd0VCL3dRRUF3SUNwREFQCkJnTlZIUk1CQWY4RUJUQURBUUgvTU
.........
```
і це фактично буде те саме, що знаходиться в конфіг файлі: `~/.kube/config`, що використовується при доступі до кластеру.
Ці сертифікати можна декодувати, командою: `echo <значення сетифікату> | base64 -d > <файл куди його зберігти>`
В цьому конфігу зберігається CA сертифікат, сертифікат клієнта та його ключ (зазвичай файли ca, crt, key).
Тепер до серверу можна спробувати підлючитися, командою:
```
curl https://<IP>:6443 --cacert <ca> --cert <crt> --key <key> 
```
Якзо все пішло гаразд ти ми отримаємо перелік URL які доступні на сервері.
Проте без вказівки ca, crt, key - ми не отримаємо доступу до серверу.

# Зовінішній доступ
Переглянувши сервіси з простору за замовчуванням, ми побачимо існуючий сервіс kubernetes:
```
kubectl get svc

NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   260d
```
Якщо його відредагувати: `kubectl edit svc`
```
kubectl edit svc

apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2023-09-18T06:10:06Z"
  labels:
    component: apiserver
    provider: kubernetes
  name: kubernetes
  namespace: default
  resourceVersion: "243"
  uid: 0dab22b2-9f26-4aa0-bed4-ba5f7f33a3c8
spec:
  clusterIP: 10.96.0.1
  clusterIPs:
  - 10.96.0.1
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: 6443
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}
```
А саме змінити `type: ClusterIP` на `type: NodePort`.
Після чього можемо перевірити, що опис сервіса змінився:
```
kubectl get svc

NAME         TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)         AGE
kubernetes   NodePort   10.96.0.1    <none>        443:31947/TCP   260d
```
Далі пробуємо підлючитися до сервісу, де 10.241.24.26 адреса ноди, 31947 - порт, що можна побачити в описі:
```
curl https://10.241.24.26:31947 -k
```
Маємо відповідь, що анонімний доступ заборонений.
```
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "forbidden: User \"system:anonymous\" cannot get path \"/\"",
  "reason": "Forbidden",
  "details": {},
  "code": 403
}
```
І що головне, цей порт доступний на всіх нодах, що входять до кластеру.
Тепер, якщо взати конфіг клієнта та зберігти його в файл:
```
kubectl config view --raw > test.conf
```
А потім замінити строку вигляду (точніше вказати інший порт):
```
    server: https://kuber0101.bs.local.erc:6443

```
На той порт що бачимо в описі сервісу
```
    server: https://kuber0101.bs.local.erc:31947

```
То можна використавши конфіг отримати доступ до серверу:
```
kubectl get nodes --kubeconfig test.conf
```
Проте при доступі з інших ІР адрес, нод, що входять в кластер, отримаємо помилку, що сертифікат не валідний "tls: failed to verify certificate: x509"
Для того, що побачити для яких хостів був створений сертифікат, можна на головній ноді, можна виконати команду:
```
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -text
```
В частині, що наведена нижче, показаний опис, для яких хостів валідний сертифікат (частина виводу пропущена).
```
...
            X509v3 Subject Alternative Name:
                DNS:kuber0101, DNS:kuber0101.bs.local.erc, DNS:kubernetes, DNS:kubernetes.default, DNS:kubernetes.default.svc, DNS:kubernetes.default.svc.cluster.local, IP Address:10.96.0.1, IP Address:10.225.24.26
...
```
Тут бачемо головне, що сертифікат валідний на імені kubernetes.
Якщо в коніг прописати такий варіант:
```
    server: https://kubernetes:31947
```
А потім додати відповідний запис в hosts то можна отримамти доступ з будь якої ноди.

# Обмеження редагування нод NodeRestriction
Якщо в файл /etc/kubernetes/manifests/kube-apiserver.yaml, додати до аргументів запуску `--enable-admission-plugins=NodeRestriction`, то можна ввімкнути модуль контролю доступу до редагування міток нодів та подів, таким чином, що ви зможете редагувати лише локальні мітки.

Цей модуль доступу обмежує редагування об’єктів Node і Pod, які kubelet може змінювати. Щоб мати змогу редагувати вказані об'єкти з цим модулем доступу, kubelets має використовувати облікові дані в групі користувача пов'язаного з роллю типу system:nodes у формі system:node:<nodeName>. В такому випадку kubelets буде дозволено лише змінювати їхній власний об’єкт API Node і лише ті об’єкти API Pod, які прив’язані до їх вузла. kubelets не дозволено оновлювати або видаляти дані не зі свого об’єкта Node.
(документація)[https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/]



