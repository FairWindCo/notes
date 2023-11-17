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



--------------------
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
Namespaced			Non Namespaced
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



