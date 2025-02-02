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

якщо вже була спроба встановити то можливо виникнення помилки типу
/var/lib/etcd is not empty

в такому разі змінюємо команду для ігнорування попереджень:
`kubeadm init --apiserver-advertise-address=<master-node-ip> --pod-network-cidr=<pod-network> --ignore-preflight-errors=all`
приклад:
`kubeadm init --apiserver-advertise-address=95.217.134.250 --pod-network-cidr=172.16.0.0/16  --ignore-preflight-errors=all`


Після завершення встановлення бачимо код, що потрібно виконати, це щось типу такого:
це код створення конфігу для kubectl
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Для користувача root:
`export KUBECONFIG=/etc/kubernetes/admin.conf`


для підключення інших робочих нод використовуємо код що має такий вигляд:
`kubeadm join <master-node-ip> --token <token> --discovery-token-ca-cert-hash sha256:<hash>`
значення хещів та токенів зразу можна побачити після завершення розгортання головної ноди (прямо в виводі команди розгортання) або окремо запитувати про них кластер


Проте якщо зразу перевірити кластер то маємо такий стан:
`kubectl get nodes`
```
NAME    STATUS     ROLES
master  NotReady   control-plane,master
worker  NotReady   <none>
```
Всі ноди в стані не готово бо не встановлена система мережі CNI кластеру її треба встановлювати окремо.

Install calico:
```
curl https://docs.projectcalico.org/manifests/calico.yaml -O
kubectl apply -f calico.yaml
```
після цього виконуємо команду
`watch -n 1 kubectl get nodes`
та дивимось як ноди переходять в стан Ready 

КЛАСТЕР ВСТАНОВЛЕНО


## МЕРЕЖЕВІ ПОЛІТИКИ В КЛАСТЕРІ
це набори правил (як правила фаєрволу, що регулюють поведінку трафіку в середині  кластеру та зовні по відношенню до нього).
Ці набори правил реалізують системи такі як calico, weave, flannel....

Можна обмежити Ingress\Egress  трафік для групи подів базуючись на правилах та умовах.
- Ingress - вхідний трафік до подів
- Egress - вихідний трафік

По замовченню дозволено все і всі поди бачать один одного.

Команда створення пода (для тесту):
`kubectl run pod-1 --image=nginx`
Маємо вивід, щось на зразок:
pod/pod-1 created
Файктично команда запускає образ всередині кластеру та дає йому ім'я "pod-1"

Можна відкрити порт
`kubectl expose pod <ім'я пода> --port <номер порту>`
Наприклад:
`kubectl expose pod pod-1 --port 80`

Подивитися доступні сервіси можна командою
`kubectl get svc`


Перевірити роботу тестового серверу можна підключившись до консолі ноди кластеру:
`kubectl exec <pod> -it -- bash`
а в консолі наприклад можна визвати curl pod-1, що зможе підключитися до поду та побачити тестову сторінку
Або безпосередньо виконати команду на поді:
`kubectl exec <pod> -- curl <тестове посилання>`
наприклад:
`kubectl exec pod-1 -- curl pod-2`


створюємо політику мережі:
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


Проста політика, що дозволяє трафік від одного поду до іншого:
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
Таке правило дозволяє зовнішній трафік від пода поміченого міткою pod-1 до поду поміченого міткою pod-2. Проте це відкриє лише шлях від поду-1, але немає дозволу на прийом для поду-2. Для того, щоб відкрити треба створити ще одну політику:
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

Ще одна замітка по прикладу, що наведені два правила дозволять трафік лише з под1 на под2, проте запити в зворотному боці працювати не будуть. Тобто:
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
Тут попадаємо в редактор, та додаємо в розділ metadata\labels значення "ns:prod", те саме робимо і з простором за замовчуванням:
`kubectl edit ns default`
(після виходу з редактору зміни приміняться автоматично)

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
- поди з простору імен за замовчуванням не знають про існування подів в іншому просторі, тому доступ по імені не можливий лише за ІР.
- так як політика блокувати все діє лише на простір за замовченням, то в просторі прод, дозволено будь який трафік, тому для доступу з под2 достатньо створити лише вихідне правило для трафіку і все запрацює, але лише за ІР адресою.

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


після чого перевіряємо, що все працює:
`kubectl get all -n kubernetes-dashboard`

тут бачимо деяку кількість різних об'єктів, сервіси, поди, репліки и т.п.

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
ми повинні бачити щось на зразок
```
NAME                           TYPE        CLUSTER-IP        EXTERNL-IP   PORTS(s)
.......
service/kubernetes-dashboard  NodePort    xxx.xxx.xxx.xxx    <none>       9090:<число>/TCP
```
ось це число, це й буде номер порту за яким на нодах буде організовано прослуховування.

Підключитися  до сервісу буде можна по <ІР адреса ноди>:<ПОРТ_прослуховування>


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

Тут важливо, щоб був сервіс з іменем test, який можна наприклад створити:

варіант на основі nginx
`kubectl run pod-1 --image=nginx`
`kubectl expose pod pod-1 --port=80 --name test1`

варіант на основі apache
`kubectl run pod-2 --image=httpd`
`kubectl expose pod pod-2 --port=80 --name test2`

та тестовий контролер:
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

Наступна проблема, полягає  втому, що інгрес контроллер має крім HTTP ще й HTTPS порт, проте на цьому порті за замовчуванням встановлено фейковий сертифікат.

Для того, щоб встановити свій треба його згенерувати:
`openssl req -x509 -newkey rsa:4096 -keyout key.pem out cert.pem -days 365 -nodes`

Додаємо сертифікат в якості секрета кубернетіса:
`kubectl create secret tks secure-ingress --cert=cert.pem --key=key.pem`

Після чого вносимо зміни в наш тестовий контролер:
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


Як альтернатива можна скачати "бінарніки" самостійно
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

Заходимо за посиланням на реліз:
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
отримаємо еталонний хешкод


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

В кластері є два типи ресурсів:
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
 - може читати секрети (can read the secrets)

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
Створімо два простори імен prod та deploy
- користувач test може лише дивитися секрет в просторі prod
- користувач test може лише дивитися секрет та переглядати перелік секретів в просторі deploy
- також перевіримо чи може користувач test виконувати відповідні дії (can-i)
```
kubectl create ns prod
kubectl create ns deploy
```
В просторі prod  створюємо роль менеджер секретів
`kubectl -n prod create role secret-manager --verb=get --resource=secrets`

даємо цій ролі можливість виконувати команду get для ресупсів secrets

Створюємо прив'язування ролі до користувача:
`kubectl -n prod create rolebinding secret-manager --role=secret-manager --user=test`

Тут створюється зв’язування з іменем secret-manager, де роль secret-manager прив'язується до користувача test

В іншому просторі робимо аналогічну роль
`kubectl -n deploy create role secret-manager --verb=get --verb=list --resource=secrets`

та прив'язуємо роль до користувача тільки вже в цьому просторі імен
`kubectl -n deploy create rolebinding secret-manager --role=secret-manager --user=test`

## Тестування прав
Існує спеціальна команда яка каже чи може користувач виконати певні дії з певними об'єктами

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
Для перевірки своїх прав доступу існує спеціальна команда:
Перший варіант перевіряє чи можу я створювати поди у всіх просторах імен
Другий варіант перевіряє чи може користувач test-user я бачити всі поди в просторі імен test
Третій варіант перевіряє чи можу я робити, що завгодно з чим завгодно в поточному просторі імен
Четвертий варіант показує всі дозволені дії в просторі імен test
```
kubectl auth can-i create pods --all-namespaces
kubectl auth can-i list pods -n test --as test-user
kubectl auth can-i '*' '*'
kubectl auth can-i --list --namespace=test
```
Інші корисні перевірки:
Перевірка що я можу робити все, що завгодно з усіма об’єктами в просторі default
`kubectl auth can-i '*' '*'`

Перевірка що я можу робити все, що завгодно з секретами в просторі default
`kubectl auth can-i '*' secrets`

Перевірка що я можу робити все, що завгодно з усіма обє'ктами в просторі <name-space>
`kubectl auth can-i '*' '*' -n <name-space>`

Перевірка що я можу робити все, що завгодно з секретами в протсорі <name-space>
`kubectl auth can-i '*' secrets -n <name-space>`

Перегляд всіх дозволів для вказаного простору <name-space>
`kubectl auth can-i --list -n <name-space>`


Розглянемо другий варіант, надаємо користувачу test право видаляти деплойменти у всіх просторах імен
А користувачу new видаляти деплоймент лише в просторі danger
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

тут буде відповідь yes, а для інших запитів:
```
kubectl auth can-i delete deployment --as new
kubectl auth can-i delete deployment --as new -n prod
kubectl auth can-i delete deployment --as new -n deploy
```
відповідь буде no


## Акаунти
в кластері існує два типи акаунтів
- сервісні акаунти,  найчастіше використовується машинами, такими як поди, для авторизації доступу до АРІ та зовнішніх сервісів. Самі такі сервісні акаунти створюються, змінюються і видаляються через АРІ кубера;
- та нормальні акаунти користувачів. (кожен з яких має свій сертифікат та ключ видані СА certificate authority кластера кубера, обов'язково сертифікат повинен мати CN (common name) в іменем користувача. За допомогою цих даних, можна виконувати команди в АРІ згідно з визначеними ролями.

Для організації доуступу користувача створюємо ключ:
`openssl genrsa -out intern.key 2048`

він буде в файлі intern.key

Далі створюємо CSR (Certificate Signing Request) — це ключ, який генерується при запиті на видачу сертифіката.

`openssl req -new -key intern.key -out inter.csr`

Майже всі поля заповнюємо за своїм розсудом, єдине, що важливо це значення яке ми запишемо в CN (common name).
В нашому прикладі ми назвемо користувача intern

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

А для отримання доступу запит треба підтвердити, це можна зробити командою:
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

Тепер потрібно створити контекст:
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

Сервісні акаунти
---------------------------------------------------------------------------------------------------
Сервісні акаунти, вони завжди відносяться до якогось простору імен (за замовченням це default).
Під кожний SA (сервіс акаунт) створюється секрет який зберігає АРІ ключ, та який може бути використаний для взаємодії з сервісами кубернетіс.

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

Тут цікаво, бо за інформацією автоматично повинен бути створений і секрет, що зберігає токен.
Проте в випадку версії 1.28 цього автоматично не стається.

Для створення токену слугує команда:
`kubectl create token <сервісний акаунт>`

Наприклад:
`kubectl create token test`

Версії Kubernetes до версії 1.22 автоматично створювали довгострокові облікові дані для доступу до API Kubernetes. Цей старіший механізм базувався на створенні маркерів Secrets, які потім можна було монтувати в запущені модулі. У новіших версіях, включаючи Kubernetes v1.29, облікові дані API отримують безпосередньо за допомогою API TokenRequest і монтуються в Pods за допомогою проектованого тому. Токени, отримані за допомогою цього методу, мають обмежений час життя та автоматично стають недійсними, коли видаляється Pod, до якого вони монтуються.

Проте є можливість явно створити такий токен, за старим зразком для цього застосовуємо деплоймент типу такого, де build-robot, це ім'я сервісного акаунту
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

яка на виході дає наступний вивід, що можна зберігати в файл:
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

то отримаємо json відповідь де буде сказано, що анонімний користувач не має доступу до АРІ кластеру (це тому, що був анонімний доступ).

Для того, щоб мати авторизований доступ, потрібно взяти зміст файлу token з каталогу /run/secrets/kubernetis.io/serviceaccount та вставити його в команду:
`curl https://kubernetes -k -H "Authorization: Bearer token_data"`

в цьому випадку система поверне відповідь, що доступу немає в сервісного акаунту з нашого простору імен. Далі потрібно налаштувати відповідний доступ для самого акаунту.

Проте, часто не потрібно, щоб сервісний акаунт був постійно підключений до контейнеру, для цього слугує опція "automountServiceAccountToken: false", якщо змінити деплоймент наступним чином, то побачимо, що сервісний акаунт не буде замаунчений в середині контейнера. 
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
Перевірити це можна командою:

`kubectl auth can-i delete secret --as system:serviceaccount:default:test`

де default - це простір імен в якому розміщено сервісний акаунт, а test - це сервісний акаунт від імені якого йде перевірка
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

Якщо додати до командного рядка аргумент --anonymous-auth=false, то можна керувати доступом від анонімного користувача
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

ця команда виведе, щось на зразок цього:
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
Ці сертифікати можна декодувати, командою: `echo <значення сетифікату> | base64 -d > <файл куди його зберегти>`
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
Після чого можемо перевірити, що опис сервіса змінився:
```
kubectl get svc

NAME         TYPE       CLUSTER-IP   EXTERNAL-IP   PORT(S)         AGE
kubernetes   NodePort   10.96.0.1    <none>        443:31947/TCP   260d
```
Далі пробуємо підключитися до сервісу, де 10.241.24.26 адреса ноди, 31947 - порт, що можна побачити в описі:
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
Тепер, якщо взяти конфіг клієнта та зберегти його в файл:
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
Тут бачимо головне, що сертифікат валідний на імені kubernetes.
Якщо в конфіг прописати такий варіант:
```
    server: https://kubernetes:31947
```
А потім додати відповідний запис в hosts то можна отримати доступ з будь якої ноди.

# Обмеження редагування нод NodeRestriction
Якщо в файл /etc/kubernetes/manifests/kube-apiserver.yaml, додати до аргументів запуску `--enable-admission-plugins=NodeRestriction`, то можна ввімкнути модуль контролю доступу до редагування міток нодів та подів, таким чином, що ви зможете редагувати лише локальні мітки.

Цей модуль доступу обмежує редагування об’єктів Node і Pod, які kubelet може змінювати. Щоб мати змогу редагувати вказані об'єкти з цим модулем доступу, kubelets має використовувати облікові дані в групі користувача пов'язаного з роллю типу system:nodes у формі system:node:<nodeName>. В такому випадку kubelets буде дозволено лише змінювати їхній власний об’єкт API Node і лише ті об’єкти API Pod, які прив’язані до їх вузла. kubelets не дозволено оновлювати або видаляти дані не зі свого об’єкта Node.
(документація)[https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/]
За замовченням цей плагін активований.
Перевіримо його роботу, на робочій ноді перевіряємо:
Дивимося конфігурацію підключення:
```
kubectl config view
```
Якщо на ноді не налаштоване підключення до АРІ серверу, то матимемо відповідь типу такої:
```
apiVersion: v1
clusters: null
contexts: null
current-context: ""
kind: Config
preferences: {}
users: null
```
Перевіряємо наявність файлу
```
cat /etc/kubernetes/kubelet.conf
```
Якщо він є і в вас користувач типу root, то можна створити змінну оточення:
```
export KUBECONFIG=/etc/kubernetes/kubelet.conf
```
Перевіряємо, команда для отримання переліку нод
```
kubectl get nodes
```
якщо все гаразд до бачимо щось на зразок:
```
NAME            STATUS   ROLES           AGE    VERSION
graylog0001     Ready    <none>          260d   v1.28.2
graylog0101     Ready    <none>          260d   v1.28.2
graylog0201     Ready    <none>          260d   v1.28.2
kuber0101       Ready    control-plane   260d   v1.28.2
kuber0201       Ready    control-plane   260d   v1.28.2
mediawiki0101   Ready    <none>          260d   v1.28.2
mediawiki0201   Ready    <none>          260d   v1.28.2
```
тепер намагаємося отримати перелік простори імен
```
kubectl get ns
```
І тут бачимо таку помилку:
```
Error from server (Forbidden): namespaces is forbidden: User "system:node:graylog0001" cannot list resource "namespaces" in API group "" at the cluster scope
```
в нашому випадку робоча нода це graylog0001 і їй заборонено переглядати протори імен.
Спробуємо поставити мітку на іншу ноду:
```
kubectl label node graylog0201 cks/test=yes
```
Теж отримуємо помилку, що нам це заборонено:
```
Error from server (Forbidden): nodes "graylog0201" is forbidden: node "graylog0001" is not allowed to modify node "graylog0201"
```
Крім цього заборонено навіть змінювати локальні мітки, що починаються з node-restrictions.kubernetes.io.
```
kubectl label node graylog0001 node-restrictions.kubernetes.io/test=yes
Error from server (Forbidden): nodes "graylog0001" is forbidden: is not allowed to modify labels: node-restrictions.kubernetes.io/test
```
Цей модуль підвищує безпеку кластеру.

# Оновлення кластеру
Найчастіше є такі причини оновити кластер:
- виправлення помилок
- оновлення безпеки
- необхідна специфічна версія для продукту, що використовується
- необхідна підтримка певних функцій (останній реліз)

  Версія сладається з трьох чисел major.minor.patch (наприклад 1.19.2 major=1, minor=19, patch=2).
  minor - змінюється кожні три місяці.

## алгоритм оновлення
- в першу чергу оновлюються основні компоненти, а саме api-server, controller-manager, scheduller
- в другу чергу робочі компоненти, а саме kubectl, kube-proxy
всі компоненти повинні мати однакову minor версію з api-server (або на один реліз менше).

## алгоритм оновлення ноди
1. в першу чергу потрібно виконати команду:
```
kubectl drain <node>
```
яка безпечно прибере всі поди з вибраної ноди, а також заборонить розміщення нових подів.
2. Після чого оновлюємо компоненти.
3. А потім повертаємо ноду в роботу.
```
kubectl uncordon <node>
```
### Оновлення головної ноди
1. зупиняємо її роботу
Практично є певні особливості при оновленні головної ноди, можна отримати помилку, що її не можливо зупинити, щоб це обійти до команди додається --ignore-daemonsets. Якщо цю опцію не додати, то нода стане зі статусом Ready,SchedulingDisable. Тому для повної зупинки використовуємо:
`kubectl drain <node> --ignore-daemonsets` і чекаємо її завершення.

2. далі оновлюємо компоненти:
`apt install kubeadm=<ver> kubelet=<ver> kubectl=<ver>`

доступні версії можна побачити apt-cache show kubeadm | grep 1.20
В прикладі припустимо в нас є кластер версії 1.19 то ми хочемо його оновити на 1.20, тому й шукаємо доступні версії.
Виконуємо оновлення версій. Та перевіряємо встановлені версії.
```
kubeadm version
```
3. Виконуємо план оновлення
```
kubeadm upgrade plan
```
Далі в плані оновлення шукаємо команду 
```
kubeadm upgrade apply v<version>
```


### Оновлення робочьої ноди
1. зупиняємо її роботу
Практично є певні особливості при оновленні ноди, можна отримати помилку, що її не можливо зупинити, щоб це обійти до команди додається --ignore-daemonsets. Якщо цю опцію не додати, то нода стане зі статусом Ready,SchedulingDisable. Тому для повної зупинки використовуємо:
`kubectl drain <node> --ignore-daemonsets` і чекаємо її завершення.

2. далі овновлюємо компоненти:
`apt install kubeadm=<ver>`

доступні версії можна побачити apt-cache show kubeadm | grep 1.20
В пракладі припустимо в нас є кластер версії 1.19 то ми хочемо його оновити на 1.20, тому й шукаємо доступні версії.
Виконуємо оновлення версій. Та перевіряємо встановлені версії.
```
kubeadm version
```
3. Виконуємо оновлення
```
kubeadm upgrade node
```
4. далі оновлюємо компоненти:
`apt install kubelet=<ver> kubectl=<ver>`

Поновлюємо роботу всіх нод.
Фактично головна нода залишається зупиненої, до поки не оновлені всі інші.

# Секретні дані (паролі)
Подивитися секрети, що існують в системі можна командою: `kubectl get secret`
Створемо кілька секретів:
```
kubectl create secret generic secret1 --from-literal user=admin
kubectl create secret generic secret2 --from-literal pass=1234
kubectl create secret generic backend-user --from-literal=backend-username='backend-admin'
```
таку інформацію можна задіяти при створенні пода, в якості пристрою, що монтоється, для цього слугує такий опис:
```
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mypod
    image: redis
    env:
    - name: SECRET_USERNAME
      valueFrom:
        secretKeyRef:
          name: backend-user
          key: backend-username
    volumeMounts:
    - name: secret_mount
      mountPath: "/etc/secret_file"
      readOnly: true
  volumes:
  - name: secret_mount
    secret:
      secretName: secret1
      optional: true
```
В цьому описі secret1, монтується в якості файлу /etc/secret_file. 
Крім того, ще один засіб застосування секретів це передача секрета як змінну оточення. Створюється змінна SECRET_USERNAME з секрета backend-user, з ключа backend-username.
Подивитися змінні, що передаються в середину поду, можна командою:
`kubectl.exe exec <назва поду> -- env`, крім того можна подивитися всі змонтовані файлові системи `kubectl exec <назва поду> -- mount`
```
kubectl -n graylog exec graylog-0 -- env
kubectl -n graylog exec graylog-0 -- mount
```
(концепція секретів)[https://kubernetes.io/docs/concepts/configuration/secret/]
Щоб розібратися в тому, що використовує образ докеру, потрібно виконати кілька дій.
Знайти робочу ноду на якій запущений необхідна нода. Для цього слугує наступна команда: 
`kubectl -n graylog get pods -o wide`. Вона дає такий результат:
```
kubectl -n graylog get pods -o wide
NAME               READY   STATUS      RESTARTS       AGE    IP               NODE            NOMINATED NODE READINESS GATES
graylog-0          1/1     Running     0              18h    172.27.102.142   graylog0201     <none>           <none>
graylog-1          1/1     Running     0              18h    172.27.50.213    graylog0101     <none>           <none>
```
Тут видно робочу ноду.
Якщо перейти на робочу ноду то можна дізнатися які контейнери там працюють (для докеру служить команда docker, а для containerd команда crictl):
```
crictl ps
docker container ls
```
Вони дають результати схожі на ці:
```
CONTAINER           IMAGE             CREATED             STATE         NAME            ATTEMPT     POD ID              POD
beb4e3ae72a2a       f6bb497cd9bd7    19 hours ago        Running       graylog          0           b6d3b84d9c8a1       graylog-2
f6ffdc88fc28b       aacc2e9d283d5    25 hours ago        Running       opensearch       0           b34f42ba3a3cd       graylog-opensearch-cluster-masters-2
```
тут головне це перша колонка з ідентифікаторами контейнерів.
Знаючи цей ідентифікатор можна подивитися опис контейнеру:
```
crictl inspect <ідентифікатор>
docker inspect <ідентифікатор>
```
Ця команда виводить інформацію про структуру контейнеру, які змінні використовуються, які команди запускаються, які файлові системи монтуються.
Всі секрети зберігаються всередині сервіса ETCD, взаємодія з ним відбувається через API SERVER, з яким безпосередньо взаємодіє сервіс KUBELET, який передає дані до DOCKER/CONTAINERD. ETCD та API SERVER розміщені на головній ноді, а KUBELET та DOCKER на робочій. Таким чином ланцюг взаємодії такий: DOCKER/CONTAINERD <--> KUBELET <--> API SERVER <--> ETCD Існує спеціальний клієнт для etcd, його можна поставити командою:
Існує спеціальний клієнт для etcd, його можна поставити командою:
```
apt install etcd-client
```
Якщо спробувати підключитися до клієнту:
```
etcdctl endpoint health

{"level":"warn","ts":"2024-06-05T13:37:26.529+0300","caller":"clientv3/retry_interceptor.go:62","msg":"retrying of unary invoker failed","target":"endpoint://client-e87757f5-1f7c-4d55-910a-25722f779e2e/127.0.0.1:2379","attempt":0,"error":"rpc error: code = DeadlineExceeded desc = latest balancer error: all SubConns are in TransientFailure, latest connection error: connection closed"}
127.0.0.1:2379 is unhealthy: failed to commit proposal: context deadline exceeded
```
Проте отримаємо помилку, бо в нас не має сертифікатів для підлючення. В якості необхідних ключів використаємо ключі від apiserver, які він і використовує для роботи з etcd. Тоді команда буде мати наступний вигляд:
```
ETCDCTL_API=3 etcdctl --cert /etc/kubernetes/pki/apiserver-etcd-client.crt --key  /etc/kubernetes/pki/apiserver-etcd-client.key --cacert /etc/kubernetes/pki/etcd/ca.crt endpoint health

127.0.0.1:2379 is healthy: successfully committed proposal: took = 29.487076ms
```
Маємо робочу відповідь.
Тепер можна подивитися як зберігаються секрети в ETCD:
```
ETCDCTL_API=3 etcdctl --cert /etc/kubernetes/pki/apiserver-etcd-client.crt --key  /etc/kubernetes/pki/apiserver-etcd-client.key --cacert /etc/kubernetes/pki/etcd/ca.crt get /registry/secrets/default/secret2
```
Отримаємо приблизн таку відповідь:
```
/registry/secrets/default/secret2
k8s


v1Secret?
?
secret2?default"*$8d257411-a8c3-4298-9f36-2181c366ec8f2蹀??a
kubectl-createUpdate?v蹀?FieldsV1:-
+{"f:data":{".":{},"f:pass":{}},"f:type":{}}B

pass1234?Opaque?"
```
Але головний момент полягіє в тому, що ці данні зберігаються в незашифрованому вигляді. Тобто це загроза безпеки.
Туму для захисту такої інформації можна примінити шифрування.
(документація з цього приводу)[https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/]
Створюємо конфігурацію для шифрування серкетів (опис взято з документації):
Всього є два провайдери шифрування aescbc та identity. Тут потрібно обов'язково вставити пароль закодований в base64. Причому пароль повинен бути від 16 до 64 символів. Команда для кодування: `echo -n <пароль> | base64`
```
---
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <BASE 64 ENCODED SECRET>
      - identity: {} # REMOVE THIS LINE
```
Створрюємо файл наприклад такий `/etc/kubernetes/etcd/enc.yaml` зі змістом наведеним вище, далі потрібно змінити налаштування /etc/kubernetes/manifests/kube-apiserver.yaml додати параметр `--encryption-provider-config=/etc/kubernetes/etcd/enc.yaml` в команду запуску, а також створити записи для volumeMounts та volumes, що будуть вказувати на каталог ді зберігається конфігурація провайдера шифрування.
Вийде приблизно так:
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
    - --encryption-provider-config=/etc/kubernetes/etcd/enc.yaml
    - --advertise-address=10.225.24.26
    - --allow-privileged=true
    - --authorization-mode=Node,RBAC
......
    volumeMounts:
    - mountPath: /etc/kubernetes/etcd
      name: etcd-enc
      readOnly: true
......
  volumes:
  - hostPath:
      path: /etc/kubernetes/etcd
      type: DirectoryOrCreate
    name: etcd-enc
......
```
Після зміни цього файлу, автоматично відбудеться перезагрузка сервісу та через кілька хвилин він стане доступним.
Тепер якщо подивитися тепер то секрети будуть не закодовані. Кодуватися будуть лише нові секрети.
Для того, щоб закодувати вже існуючи їх треба перестворити, це можна зробити командою:
```
kubectl get secrets -A -o yaml | kubectl replace -f -
```
Після чого все буде зашифровано.
# RuntimeClass
RuntimeClass - це фіча Kubernetes, яка дозволяє вказати рантайм контейнера для ваших робочих навантажень. За допомогою RuntimeClass можна вибирати між різними рантаймами контейнера або різними конфігураціями одного і того ж рантайму. Це корисно для безпеки, оскільки різні рантайми відрізняються за властивостями безпеки. Наприклад, ви можете використовувати легкий рантайм для деяких робочих навантажень, що потребують швидкого запуску, і більш безпечний рантайм (але з додатковими накладними витратами) для робочих навантажень, які потребують більш високого рівня ізоляції.
Ще однією перевагою RuntimeClass є те, що він дозволяє перемикати рантайми без зміни робочих навантажень. Наприклад, якщо вам потрібно перейти на безпечніший рантайм, ви можете просто оновити RuntimeClass в маніфесті деплою робочого навантаження, і Kubernetes автоматично буде використовувати новий рантайм, пов'язаний з цим RuntimeClass.
Загалом, RuntimeClass надає потужний інструмент для управління середовищем рантайму робочих навантажень Kubernetes, забезпечуючи підвищений контроль за безпекою та гнучкістю.
(документація)[https://kubernetes.io/docs/concepts/containers/runtime-class/]
Для активації RuntimeClass порібно виконати кілька дій:
1. Активувати налаштування RuntimeClass
   для containerd необідно додати в файл `/etc/containerd/config.toml` розділ `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.${HANDLER_NAME}]`, в якому задаються налаштування.
3. Створити маніфест RuntimeClass
Створюємо файл такого змісту та приміняємо його на кластер
```
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  # The name the RuntimeClass will be referenced by.
  # RuntimeClass is a non-namespaced resource.
  name: myclass 
# The name of the corresponding CRI configuration
handler: myconfiguration 
```
де myclass - це назва RuntimeClass, що ми створюємо, а myconfiguration - відповідна назва конфігурації (яка задана в конфігах)
3. Задіяти відповідний RuntimeClass на подах
```
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  runtimeClassName: myclass
  # ...
```
Задіюємо myclass при роботі даного пода.

# Зміна користувача та групи під якими працює контейнер
За замовченням контейнер запущений під користувачем 0 (root) та групою 0 (root). Це можна легко перевірити, якщо творити тестовий маніфест:
```
kubectl run test-pod --image=busybox --command -o yaml --dry-run=client > test-pod.yaml -- sh -c 'sleep 1d'
```
отримаємо приблизно такий маніфест:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test-pod
  name: test-pod
spec:
  containers:
  - command:
    - sh
    - -c
    - '''sleep'
    - 1d'
    image: busybox
    name: test-pod
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
Якщо його застосувати: `kubectl apply -f test-pod.yaml`, а потім підлючитися `kubectl exec it test-pod -- sh` або просто виконати команду:
`kubectl exec -it test-pod -- id`, то отримаємо під яким користувачем працює контейнер, приблизно такі: `uid=0(root) gid=0(root) groups=10(wheel)`

Це можна змінити, якщо додати в опис поду securityContext, як показано нижче:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test-pod
  name: test-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
...
```
Тепер под буде працювати ід імені користувача `uid=1000 gid=3000 groups=2000`
(контексти безпеки)[https://kubernetes.io/docs/tasks/configure-pod-container/security-context/]
Іншим розділом де можна задати контекст безпеки є частина containers, по типу такого:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test-pod
  name: test-pod
spec:
  containers:
  - command:
    - sh
    - -c
    - '''sleep'
    - 1d'
    image: busybox
    securityContext:
       runAsNonRoot: true
    name: test-pod
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
Що головне, що ці параметри мають більший пріорітет ніж параметри на рівні поду, крім того тут доступні такіж самі значення runAsUser та runAsGroup.
Крім того тут є додатковий параметр readOnlyRootFilesystem, що змонтує рутову файлову систему контейнеру в рижимі лише для читання. А параметр allowPrivilegeEscalation: false, введе заборону на отримання більших прав ніж у батьківського процесу.
Цікаво, що якщо задеплоїти опис наведений вище, то контейнер не запуститься, з помилкою, що контейнер буде запущено не під рутом, а от сам образ повинен працювати під рутом.
Проте навіть якщо под працює під користувачем root, то все одно всередині контейнеру немає доступу до встановлення змінниих я ядра, команди на зразок: `systemctl kernel.hostname=test`, отримаємо помилку, що файлова система в рижмі лише для читання. Для того, щоб це запрацювало потрібно додати такий контекст безпеки:
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test-pod
  name: test-pod
spec:
  containers:
  - command:
    - sh
    - -c
    - '''sleep'
    - 1d'
    image: busybox
    securityContext:
       privileged: true
       #allowPrivilegeEscalation: true
    name: test-pod
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```
В режимі privileged користвувач root в середині контейнеру точно відповідає root на сервері.

## Глобальні політики безпеки
Починаючи з версії 1.25, є маханізм глобальих обмежень, що вмикається шляхом встановлення спеціальних міток на рівні простору імен:
(pod-security-admission)[https://kubernetes.io/docs/concepts/security/pod-security-admission/]
існують дві спеціальні мітки:
```
# The per-mode level label indicates which policy level to apply for the mode.
#
# MODE must be one of `enforce`, `audit`, or `warn`.
# LEVEL must be one of `privileged`, `baseline`, or `restricted`.
pod-security.kubernetes.io/<MODE>: <LEVEL>

# Optional: per-mode version label that can be used to pin the policy to the
# version that shipped with a given Kubernetes minor version (for example v1.30).
#
# MODE must be one of `enforce`, `audit`, or `warn`.
# VERSION must be a valid Kubernetes minor version, or `latest`.
pod-security.kubernetes.io/<MODE>-version: <VERSION>
```
- enforce - Порушення політики призведуть до відхилення модуля.
- audit - Порушення політики аудиту призведуть до додавання анотації аудиту до події, записаної в журналі аудиту, але в інших випадках допускаються.
- warn - Порушення політики призведуть до попередження користувача, але в інших випадках це дозволено.
- privileged - Політика Privileged Unrestricted, що забезпечує максимально широкий рівень дозволів. Ця політика дозволяє відомі ескалації привілеїв.
- baseline - Базовий рівень Мінімально обмежувальна політика, яка запобігає відомим підвищенням привілеїв. Дозволяє стандартну (мінімально задану) конфігурацію Pod.
- restricted - Обмежено Сильно обмежена політика, дотримуючись поточних передових методів зміцнення контейнерів.
(налаштування)[https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-admission-controller/#configure-the-admission-controller]
```
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: PodSecurity
  configuration:
    apiVersion: pod-security.admission.config.k8s.io/v1 # see compatibility note
    kind: PodSecurityConfiguration
    # Defaults applied when a mode label is not set.
    #
    # Level label values must be one of:
    # - "privileged" (default)
    # - "baseline"
    # - "restricted"
    #
    # Version label values must be one of:
    # - "latest" (default) 
    # - specific version like "v1.30"
    defaults:
      enforce: "privileged"
      enforce-version: "latest"
      audit: "privileged"
      audit-version: "latest"
      warn: "privileged"
      warn-version: "latest"
    exemptions:
      # Array of authenticated usernames to exempt.
      usernames: []
      # Array of runtime class names to exempt.
      runtimeClasses: []
      # Array of namespaces to exempt.
      namespaces: []
```
Є певні операції в контейнерах, які можуть вимагати особливі привілеї, наприклад використання файєрволу
Для прикладу якщо створити такий контейнер bisybox, з командою:
```
  - command:
    - sh
    - -c
    - 'apt get update && apt-get install iptables -y && iptables -L && sleep 1d'
```
Т він не запуститься, а отримає помилку, для того, щоб її виправити потрібно додати до опису контейнеру частину з: `["NET_ADMIN", "SYS_TIME"]`, тат головний параметр NET_ADMIN, який дозволить контейнеру отримати доступ до адміністрування мережевими налашуваннями ядра.
```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  containers:
  - name: sec-ctx-4
    image: bisybox
    securityContext:
      capabilities:
        add: ["NET_ADMIN", "SYS_TIME"]
```
# Зменщення розмірів образів
Створемо тестовий контейнер, для цього запишемо такий файл Dockerfile:
```
FROM ubuntu
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y golang-go
COPY app.go .
RUN CGO_ENABLED=0 go build app.go
CMD ["./app"]
```
Поруч створемо файл app.go, що містить таку тестову програме на ГО.
```
package main

import {
   "fmt"
   "time"
   "os/user"
}

func main () {
   user, err := user.Current()
   if err != nil {
     panic(err)
   }

   for {
       fmt.Println("user: " + user.Username + " id: " + user.Uid)
       time.Sleep(1 * time.Second)
   }
}
```
Якщо зібрати такий образ командою `docker build -t app .`, то в результаті отримаємо образ майже 700Мб розміром. (Розмір можна побачити командою `docker image ls`). Проте якщо змінити Dockerfile:
```
FROM ubuntu
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y golang-go
COPY app.go .
RUN CGO_ENABLED=0 go build app.go

FROM alpine
COPY --from=0 /app .
CMD ["./app"]
```
В такому випадку ми переходимо до побудову образу кількома стадіями. Спочатку створюється тимчасовий образ на першій стадії, а потім на другій стадії використовується маленький образ в який командою `COPY --from=0 /app .` переноситься пободований бінарний файл, а темчасовий образ потім видаляється. В результаті результуючий образ буде приблизно 8Мб. Таким чином значно зменшеться місце яке він займає на диску.

Головною проблемою нашого нового образу є те, що в ньому процес запущено від імені користувача root і хоче це середовище ізольоване проте це не є гарною практикою. Крім того у вихідному продуктовому образі вказана залежність від останньої версії alpine, проте з часом цей образ може бути замінено на новий, що не в деяких випадках може зробити нашу програму не робочою. Щоб цього уникнути гарною практикою буде вказати конкретну версію образу яка необхідна для запуску. Наступної гарної практикою буде створити користувача і запустити наш процес під ним. Крім того, для підвищення безпеки образу можна додати ще кілька кроків. Перший крок це забрати права на запис з папки etc, для всіх користувачів. Другий більш радикальний це видалити утиліти з папки bin, разом з самим шелом, що не дозволить взагалі підключатися до вибраного образу. Проте така поведінка потребує зваженого підходу, адже і сам процес може потребувати деякі інструменти з цієї папки, а також це може дуже сильно завадити пошуку проблем в роботі сервісу (тому, що немає утиліт командного рядка).

Змінемо трохи опис образу:
```
FROM ubuntu
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y golang-go
COPY app.go .
RUN CGO_ENABLED=0 go build app.go

FROM alpine:3.14.2
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h /home/appuser
RUN chmod a-w /etc
RUN rm -rf /bin/*
COPY --from=0 /app /home/appuser
USER appuser
CMD ["./app"]
```
Тут треба звернути на кілька моментів: 
- для образу задано версію базового образу, що дозволяє точно забезпечити все необхідне, щоб потім не було несподіванки.
- перша команда RUN, що виконується при побудові образу, створює користувача.
- команда USER змінює поточного користувача на вказанного (до цього всі дії виконувалися під рутом), таким чином программа буде виконана з правами користувача appuser.
- крім того тут додана команда друга команда RUN, що відміняє дсотуп всік користувачів крім root, на запис в каталог /etc
- третя команда RUN видаляє всі бінарні утиліти з каталога /bin, а тому числі і шел sh. Що не дозволить підлючитися до контецнеру в режимі шелу. Це підвищує безпеку контейнеру, так як прибирає не потрібні утиліти, які можуть бути використані при взломі контейнеру.

# OPA (Open Policy Agent) системи політик
Kubernetes має механізм інтегації систем політик, проте саму інструменти політик, які виконані яд двіжок політик, розробляються сторонніми організаціями.
Policy engines (движки політики) – це потужний інструмент, який Kubernetes використовує для управління та застосування політик у всьому кластері. Двигуни політики дозволяють адміністраторам кластера налаштовувати та впроваджувати їх для широкого спектру дій, включаючи доступ до мережі, використання ресурсів та розміщення подів. Прикладами двигунів політики є Open Policy Agent (OPA) та Kyverno. 

Kyverno - це двигун політики Kubernetes, який дозволяє застосовувати політики для ваших кластерів Kubernetes. За допомогою Kyverno ви можете створювати політики, що обмежують доступ до ресурсів, застосовують угоди про імена, що обмежують доступ до мережі тощо. Ви також можете визначити політики, які ініціюються за певних подій, наприклад, при створенні нового деплою. Коли відбувається порушення політики, Kyverno може вжити автоматичних дій для усунення проблеми, наприклад, заблокувати деплою або видалити під.

Однією з переваг Kyverno є те, що він легко інтегрується з Kubernetes, тому ви можете визначати політики, використовуючи знайомі об'єкти Kubernetes, такі як ConfigMaps та CRD [Custom Resource Definition – спеціальний ресурс у Kubernetes, який дозволяє вносити будь-які дані]. Kyverno також підтримує можливість валідації та генерації політики, тому ви можете легко переконатися, що ваші політики працюють так, як очікується, та генерувати їх на основі існуючих ресурсів Kubernetes.
## Встановлення OPA Gatekeeper
Перша за все перевіряємо файл /etc/kubernetes/manifests/kube-apiserver.yaml, нас цікавить параметр `- --enable-admission-plugins=NodeRestriction`, тут не повинно бути жодних інших плагінів, крім NodeRestriction.
(Gatekeeper)[https://open-policy-agent.github.io/gatekeeper/website/docs/install]
Перед цим перевіряємо, що Ваш користувач має права адміністратора кластеру:
```
  kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole cluster-admin \
    --user <YOUR USER NAME>
```
Робимо деплой плагіну:
```
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.16.3/deploy/gatekeeper.yaml
```
Про всяк випадок, команда видалення:
```
kubectl delete -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.16.3/deploy/gatekeeper.yaml
```
При встаноелнні плагіну буде створено спеціальні поди в просторі імен gatekeeper-system, а також сервіс gatekeeper-webhook-service.
Інформацію стосовно різних плагінів керування доступом, можна знайти в документації (Dynamic Admission Control)[https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/]
(Admission webhooks) Вебхуки доступу — це зворотні виклики HTTP, які отримують запити на доступ і виконують певні дії з ними. Ви можете визначити два типи веб-хуків доступу: перевіряючий веб-хук і змінюючий веб-хук. Першими викликаються веб-хуки, що змінюють доступ, і можуть змінювати об’єкти, надіслані на сервер API, щоб застосувати спеціальні параметри за замовчуванням. Після завершення всіх модифікацій об’єкта та перевірки вхідного об’єкта сервером API запускаються перевіряючі веб-перехоплювачі доступу, які можуть відхиляти запити на застосування спеціальних політик.

Веб-хуки доступу, яким потрібно гарантувати, що вони бачать кінцевий стан об’єкта, щоб застосувати політику, повинні використовувати перевіряючий веб-хук доступу, оскільки об’єкти можуть бути змінені після того, як їх побачать веб-хуки, що змінюють.
Створюємо шаблон політик безпеки:
```
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8salwaysdeny
spec:
  crd:
    spec:
      names:
        kind: K8sAlwaysDeny
      validation:
        # Schema for the `parameters` field
        openAPIV3Schema:
          type: object
          properties:
            message:
              type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8salwaysdeny
        violation[{"msg": msg}] {
          1 > 0
          msg := input.parameters.message
        }
```
А потім створюємо політику, тут є специфічний момент в шаблоні задано ім'я K8sAlwaysDeny, політика має тип `kind: K8sAlwaysDeny`.
```
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAlwaysDeny
metadata:
  name: pod-always-deny
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    messages: "ACCESS DENIED!"
```
Сама політика вибирає ресурс до якого вона буде застосована, та в данному випадку повідомлення яке буде видано при її застосуванні. В шаблоні прописана умова "1 > 0" - яка завжди виконується, тобто політка, що завжди застосована. Якщо змінити умову на "2 > 1", то отримаємо паолітику, що не буде застосована взагалі, тобто отримаємо шаблон завжди дозволено.
Перевірити шаблони та обмеження можна перевірити командами:
```
kubectl get constrainttemplates
kubectl get <ConstraintTemplate name>
kubectl get constraints
```
При застосуванні описаних вище шаблонів та політик, буль яка спроба створити под, буде заборонена.
Якщо трохи змінити частину перевірки умов, то можна оримати політику, що вимагає при створенні об'єкту задавати обов'яскові імена.
```
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("you must provide labels: %v", [missing])
        }
```
А якщо створити таку поітику:
```
metadata:
  name: ns-must-have-gk
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    # Note that "labels" is now an array item, rather than an object
    - labels: ["gatekeeper"]
```
Така політика вимагає, щоб кожний простір імен який створюється обов'язово мав мітку gatekeeper.
(Документація)[https://open-policy-agent.github.io/gatekeeper/website/docs/]


# засіб аналізу файлів розгортаньKubeSec.IO
Спеціалізованний інстурмент для аналізу безпеки деплоймент файлів (KubeSec)[https://kubesec.io/]. Якщо його встановити в якості утиліти чи контейнеру, то за його допомогою можна аналізувати файли перед їх деплоєм на загально прийняти норми безпеки.
Наприклад якщо скачати утиліту і запустити її `kubesec scan k8s-deployment.yaml`, то можна отримати рекомендації по покращеннб безпеки, наприлад додавання таких параметрів як запуск в не рутовому оточені, встановленні обмежень по пам'яті і т.п.
Крім того його можна запустити прямо з докеру:`docker run -i kubesec/kubesec:512c5e0 scan /dev/stdin < file_name_to_scan`

# Засіб тестування ConfTest
Фремворк для тестування (ConfTest)[https://www.conftest.dev/] дозволяє розробити власні правиала аналізу файлів розгортань та перевіряти їх.
Наприклад ось такий тестовий набір який збірігіють в файл policy/deployment.rego, важливо розмістити в папку policy:
```
package main

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot

  msg := "Containers must not run as root"
}

deny[msg] {
  input.kind == "Deployment"
  not input.spec.selector.matchLabels.app

  msg := "Containers must provide app label for pod selectors"
}
```
Буде перевіряти що всі розгортання типу Deployment (в правилах за це відповідають такі елементи `input.kind == "Deployment"`) повинні мати обов'язково вказівку запуску в не рут оточенні та обов'язково проставлену мітку app (ща це відповідає частина `not input.spec.template.spec.securityContext.runAsNonRoot` та  `not input.spec.selector.matchLabels.app`).
Для запуску можна використати ось такий визов докера:
```
docker run --rm -v $(pwd):/project openpolicyagent/conftest test <deployemnt for test.yaml>
```
В результаті файл `<deployemnt for test.yaml>` буде первірений і поньому будуть видані результати перевірки.
Крім тестування файлів розгортань, можна тесувати також докерфайли:
```
docker run --rm -v $(pwd):/project openpolicyagent/conftest test Dockerfile --all-namespaces
```
# утиліта Trivy
Ще одна утиліта перевірки стану контейнерів (документація)[https://aquasecurity.github.io/trivy/v0.52/]. Trivy — комплексний і універсальний сканер безпеки. Trivy має сканери, які шукають проблеми з безпекою, і показує місця, де вони вони можуть виникнути.
Використати можна таким чином:
```
docker run aquasec/trivy image <test_image>
docker run aquasec/trivy image nginx
docker run aquasec/trivy image nginx:alpine
```
По результатам команди буде виконана перевірка образу, та виведена таблиця з проблемами. Вище представлено дві команди тестування nginx, перша виведе багато попереджень про безпеку, інша навпаки nginx:alpine.
Таким чином можна перевірити і сам кубернетіс.
Наприклад можна побачити всі поди кластеру командою:
```
kubectl get pods --all-namespaces
```
Потім можна побачити з чього складаєтться под:
```
kubectl describe pod kube-apiserver-master -n kube-system
```
А потім перевірити конкретний образ:
```
docker run aquasec/trivy image k8s.gcr.io/kube-apiserver:v1.21.0
```
таким чином перевіряємо ключьові компоненти на безпеку.
# цифрові відбитки образів
Використання версії в якості вказання необхідного образу є гарною практикою, проте не найбільш безпечною.

Дізнаємося які образи використовуються всередині нашого кластеру:
kubectl get pods -A -o yaml | grep image
команда виведе, щось типу такого:
```
...
  image: docker.io/calico/apiserver:v3.29.0
      imagePullPolicy: IfNotPresent
      image: docker.io/calico/apiserver:v3.29.0
      imageID: docker.io/calico/apiserver@sha256:69c1300756468b8bcdd64f600c50c11a741012c699a4768756345d0ae5dc9310
      image: docker.io/calico/apiserver:v3.29.0
      imagePullPolicy: IfNotPresent
      image: docker.io/calico/apiserver:v3.29.0
      imageID: docker.io/calico/apiserver@sha256:69c1300756468b8bcdd64f600c50c11a741012c699a4768756345d0ae5dc9310
      image: docker.io/calico/kube-controllers:v3.29.0
      imagePullPolicy: IfNotPresent
      image: docker.io/calico/kube-controllers:v3.29.0
      imageID: docker.io/calico/kube-controllers@sha256:ba3ef20f30caa855ddf00e767af973685832546582e7fa457dac14c64d3156d0
      image: docker.io/calico/node:v3.29.0
...
```
де частина   imageID: docker.io/calico/kube-controllers@sha256:ba3ef20f30caa855ddf00e767af973685832546582e7fa457dac14c64d3156d0 вказує на конкретний образ на машині (тут від нього вказано цифровий відбиток)

Якщо подивитися опис будь якого поду `kubectl describe pod kube-apiserver -n kube-syste` то можна помітити таку частину:
```
Containers:
  kube-apiserver:
    Container ID:  containerd://d366a5c52ec267d16b2fad7515827770799ddcc6bca9545118fe0ef23b247c45
    Image:         registry.k8s.io/kube-apiserver:v1.31.2
    Image ID:      registry.k8s.io/kube-apiserver@sha256:9d12daaedff9677744993f247bfbe4950f3da8cfd38179b3c59ec66dc81dfbe0
```
І ост ця частина registry.k8s.io/kube-apiserver@sha256:9d12daaedff9677744993f247bfbe4950f3da8cfd38179b3c59ec66dc81dfbe0 – вказує на конкретний образ з потрібним хешем. Цей код може бути використано в якості версії образу.

А також може бути використано навіть для конфігурацій самого кубернетісу, наприклад маніфест /etc/kubernetes/manifests/kube-apiserver.yaml містить наступні рядки:
```
    image: registry.k8s.io/kube-apiserver:v1.31.2
    imagePullPolicy: IfNotPresent
```
їх можна замінити на 
```
    image: registry.k8s.io/kube-apiserver@sha256:9d12daaedff9677744993f247bfbe4950f3da8cfd38179b3c59ec66dc81dfbe0
    imagePullPolicy: IfNotPresent
```
тоді кластер перезапуститься і буде працювати лише з цим образом і ніяким іншим.
Крім того ці відбитки можна використовувати в якості вказівки на образи в файлах деплойментах.

## Обмеження на використання образів. 
Для системи Gatekeeper можна створити обмеження на дозволені образи в середині кластеру.
Ось приклад такого обмеження k8strustedimages_template.yaml:
```
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8strustedimages
spec:
  crd:
    spec:
      names:
        kind: K8sTrustedImages
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8strustedimages

        violation[{"msg": msg}] {
          image := input.review.object.spec.containers[_].image
          not startswith(image, "docker.io/")
          not startswith(image, "k8s.gcr.io/")
          msg := "not trusted image!"
        }
```
Цей опис дозволяє використовувати в кластері лише образи docker.io та k8s.gcr.io. Таким чином образи з інших репозиторіїв  будуть не доступні.

Тепер цей опис обмежень потрібно застосовати до конкретних об’єктів, в нашому випадку до подів, це робиться за допомогою такого деплоймента all_pod_must_have_trusted_images.yaml:
```
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sTrustedImages
metadata:
  name: pod-trusted-images
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```
Спочатку застосовуємо шаблон обмежень: `kubectl apply -f k8strustedimages_template.yaml`, потім призначаємо обмеження: `kubectl apply -f all_pod_must_have_trusted_images.yaml`

Разом з gatekeeper та встановленими обмеженнями буде дозволено використовувати образи тільки з описаних репозиторіїв.


# Аналіз поведінки ні рівні хосту та на рівні контейнеру
## Перехоплення системних викликів
Для того щоб дізнатися які системні виклики виконує програма використовується утиліта strace.
Наприклад, якщо визвати `strace ls`, то отримаємо такий результат:
```
execve("/usr/bin/ls", ["ls"], 0x7ffe3bf4a9b0 /* 32 vars */) = 0
brk(NULL)                               = 0x606223654000
arch_prctl(0x3001 /* ARCH_??? */, 0x7ffc74519f70) = -1 EINVAL (Invalid argument)
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x78d4b823c000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
newfstatat(3, "", {st_mode=S_IFREG|0644, st_size=20311, ...}, AT_EMPTY_PATH) = 0
mmap(NULL, 20311, PROT_READ, MAP_PRIVATE, 3, 0) = 0x78d4b8237000
close(3)                                = 0

…..
close(1)                                = 0
close(2)                                = 0
exit_group(0)                           = ?
+++ exited with 0 +++
```
В переліку ми бачимо системні виклики та параметри. Наприклад це шляхи до файлів які викдриваються.
Інформацію про кожний системний виклик можна подивитися в хелпі https://man7.org/linux/man-pages/dir_all_alphabetic.html

Для аналізу поведінки контейнерів можна використати такий прийом, за допомогою команди можна подивитися перелік запущених контейнерів:
`sudo crictl ps` (для докеру підійде така команда: `docker ps -a`)
```
CONTAINER           IMAGE               CREATED             STATE               NAME                        ATTEMPT             POD ID              POD
aafa4c677d3bc       48cc7c24253a8       7 weeks ago         Running             calico-kube-controllers     1                   55ab4bb39233c       calico-kube-controllers-dc8cbd649-r6vgp
….
3416770087001       2e96e5913fc06       7 weeks ago         Running             etcd                        1                   3da4ff8ec8d77       etcd-crtkubm01
f711717e3ffbd       847c7bc1a5418       7 weeks ago         Running             kube-scheduler              1                   79e9317b03d32       kube-scheduler-crtkubm01
```
Потім за від слідити необхідний процес:
`ps -aux | grep etcd`
```
root       13080  4.7  1.9 11806352 103768 ?     Ssl   2024 3509:03 etcd --advertise-client-urls=https://10.253.24.31:2379 --cert-file=/etc/kubernetes/pki/etcd/server.crt --client-cert-auth=true --data-dir=/var/lib/etcd --experimental-initial-corrupt-check=true --experimental-watch-progress-notify-interval=5s --initial-advertise-peer-urls=https://10.253.24.31:2380 --initial-cluster=crtkubm01=https://10.253.24.31:2380 --key-file=/etc/kubernetes/pki/etcd/server.key --listen-client-urls=https://127.0.0.1:2379,https://10.253.24.31:2379 --listen-metrics-urls=http://127.0.0.1:2381 --listen-peer-urls=https://10.253.24.31:2380 --name=crtkubm01 --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt --peer-client-cert-auth=true --peer-key-file=/etc/kubernetes/pki/etcd/peer.key --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt --snapshot-count=10000 --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
root       13167  9.0  8.8 1740996 468936 ?      Ssl   2024 6651:16 kube-apiserver --advertise-address=10.253.24.31 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/12 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key
```
А далі до процесу можна підключитися, та отримати системні виклики які там відбуваються:
`strace -p 13080`
```
strace: Process 13080 attached
futex(0x1a553a0, FUTEX_WAIT_PRIVATE, 0, NULL…..
```

У випадку коли немає необхідності аналізувати кожен виклик окремо, можна отримати сумарну інформацію по кількості різних системних викликів, а також профілювання часу виконання. Для цього використовується команда: `strace  -cw ls`. Тоді вивід матиме такий вигляд:
```
config  custom-resources.yaml  ddup  exchangelistener-1.0.36.tgz  get_helm.sh  globalsearch  globalsearch-5.0.24.tgz_.zip  gs  gs5  gs_old  logs  test
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 23.73    0.001189          66        18           mmap
 10.57    0.000530         529         1           execve
  8.53    0.000427          61         7           mprotect
  8.41    0.000421          46         9           close
  7.71    0.000386          55         7           openat
  7.64    0.000383          47         8           newfstatat
  5.18    0.000260          51         5           read
  4.95    0.000248          82         3           brk
  4.17    0.000209          52         4           pread64
  2.41    0.000121          60         2           getdents64
  2.23    0.000112          55         2         2 statfs
  2.19    0.000110         109         1           getrandom
  2.14    0.000107         107         1           munmap
  1.99    0.000100          49         2         2 access
  1.85    0.000093          46         2           ioctl
  1.75    0.000087          43         2         1 arch_prctl
  1.10    0.000055          54         1           write
  0.88    0.000044          44         1           prlimit64
  0.86    0.000043          43         1           set_tid_address
  0.85    0.000043          42         1           rseq
  0.83    0.000042          41         1           set_robust_list
------ ----------- ----------- --------- --------- ----------------
100.00    0.005009          63        79         5 total
```

