1. Створити простір імен:
`kubectl create namespace graylog`


2. Додати auto deployment оператор для автоматичного розгортання mongodb та OpenSearch 

Опис процесу та встановлення є тут:
https://github.com/mongodb/mongodb-kubernetes-operator/


```
helm repo add mongodb https://mongodb.github.io/helm-charts
helm install community-operator mongodb/community-operator --namespace graylog
```


Опис операторів OpenSearch:
https://github.com/Opster/opensearch-k8s-operator


```
helm repo add opensearch-operator https://opster.github.io/opensearch-k8s-operator/ 
helm install  opensearch-oper opensearch-operator/opensearch-operator --version 2.3.2 -n graylog
```

Ось так можна подивитися доступні версії операторів
see verions:
`helm search repo opensearch-operator/opensearch-operator  --versions`


Перевіряємо, що контролери готові:

`kubectl get pods -n graylog`
Бачимо щось на зразок:


```
NAME                                                              READY   STATUS    RESTARTS   AGE
mongodb-kubernetes-operator-556589b7b8-rwr8k                      1/1     Running   0          5m10s
opensearch-oper-opensearch-operator-controller-manager-5852hj4m   2/2     Running   0          86s
```



2. Встановлюємо mongodb
**Важливо, щоб опис сервісу та контролер який його розгортає були в одному пространстві імен**


```
kubectl apply -f mongo/storage_class.yaml
kubectl apply -f mongo/mongo_secret.yaml
kubectl apply -f mongo/mongodb.com_v1_hostpath.yaml -n graylog
```


Далі перевіряємо:
 `kubectl get mdbc -n graylog`
Бачимо щось типу такого:

```
kubectl get mdbc -n graylog
NAME   PHASE     VERSION
mdb0   Running   6.0.5
```

Якщо так то все працює, дивимось розгортання подів:
`kubectl get pods -n graylog`

Бачимо розгорнуті поди:

```
NAME                                                      READY   STATUS    RESTARTS   AGE
mdb0-0                                                    2/2     Running   0          5m10s
mdb0-1                                                    2/2     Running   0          4m
mdb0-2                                                    2/2     Running   0          2m28s
mongodb-kubernetes-operator-556589b7b8-b97tw              1/1     Running   0          159m
opensearch-operator-controller-manager-6fdb7d9ddd-2svcz   2/2     Running   0          159m
```



4. Розгортаємо open search

Встановлюємо мітки на ножи (set labels):

```
kubectl label node graylog0001 cluster-node=true
kubectl label node graylog0101 cluster-node=true
kubectl label node graylog0201 cluster-node=true
kubectl label node graylog0101 data-node=true
kubectl label node graylog0201 data-node=true
```



```
kubectl label node graylog0201 graylog-opensearch-master="true"
kubectl label node graylog0101 graylog-opensearch-master="true"
kubectl label node graylog0001 graylog-opensearch-master="true"
kubectl label node graylog0201 graylog-opensearch-data="true"
kubectl label node graylog0101 graylog-opensearch-data="true"
```



```
kubectl label node graylog0201 service=graylog
kubectl label node graylog0101 service=graylog
kubectl label node graylog0001 service=graylog
```

Застосовуємо описи розортання:


```
kubectl apply -f opensearch/storage_class.yaml
kubectl apply -f opensearch/admin-credentials.yaml
kubectl apply -f opensearch/pv-graylog-opesearch.yaml
```


**ВАЖЛИВО: перед наступними діями всі папки повинні бути порожніми**
WARNING BEFORE NEXT STEP CLEAR DATA DIRS

`kubectl apply -f opensearch/opensearch_cluster.yaml`


5. Розгортання GrayLog

kubectl apply -f graylog/storage_class.yaml
kubectl apply -f graylog/pv-graylog-opesearch.yaml


Примітка в разі, якщо потрібно використання SSL (то можна обмежити кількість ІР адрес для пулу грейлог,  тоді створюємо опис нового полу та вказуємо куберу його використати)

5.1 With SSL certificate:
    `kubectl apply -f graylog/ippoll.yaml`
 змінити файл опису та зняти коментарі:
        
```
# cni.projectcalico.org/ipv4pools: '["graylog-pool"]'

        #        - name: GRAYLOG_WEB_ENDPOINT_URI
        #          value: https://logs.bs.local.erc/api
```


Встановити значення в описі сервісу


        
```
- name: GRAYLOG_HTTP_ENABLE_TLS
          value: "false"
```



для імпорту SSL certificate виконуємо:

`kubectl create secret tls graylog-tls-secret   --cert=graylog/graylog_cert.pem   --key=graylog/graylog.key -n graylog`


`kubectl apply -f graylog/graylog.yaml`


_Перевіряємо_
 `kubectl get pods -n graylog`
Бачимо щост типу такого:

```
NAME                                                      READY   STATUS      RESTARTS   AGE
graylog-0                                                 1/1     Running     0          27s
graylog-1                                                 1/1     Running     0          24s
graylog-2                                                 1/1     Running     0          20s
graylog-opensearch-cluster-dashboards-58bdcfd694-z7dw2    1/1     Running     0          17h
graylog-opensearch-cluster-masters-0                      1/1     Running     0          17h
graylog-opensearch-cluster-masters-1                      1/1     Running     0          17h
graylog-opensearch-cluster-masters-2                      1/1     Running     0          17h
graylog-opensearch-cluster-nodes-0                        1/1     Running     0          17h
graylog-opensearch-cluster-nodes-1                        1/1     Running     0          17h
graylog-opensearch-cluster-securityconfig-update-g4nkb    0/1     Completed   0          17h
mdb0-0                                                    2/2     Running     0          20h
mdb0-1                                                    2/2     Running     0          20h
mdb0-2                                                    2/2     Running     0          18h
mongodb-kubernetes-operator-556589b7b8-b97tw              1/1     Running     0          22h
opensearch-operator-controller-manager-6fdb7d9ddd-2svcz   2/2     Running     0          22h
```


Перевіряємо сервіси

`kubectl get service -n graylog`
Бачимо таке

```
NAME                                                     TYPE           CLUSTER-IP      EXTERNAL-IP                              PORT(S)                                                      AGE
graylog                                                  LoadBalancer   10.99.218.68    10.225.24.61,10.241.24.61,10.253.24.30   1514:32178/TCP,80:31766/TCP,12201:31413/TCP,5044:31811/TCP   71s
graylog-opensearch-cluster                               ClusterIP      10.98.145.12    <none>                                   9200/TCP,9300/TCP,9600/TCP,9650/TCP                          17h
graylog-opensearch-cluster-dashboards                    ClusterIP      10.103.62.226   <none>                                   5601/TCP                                                     17h
graylog-opensearch-cluster-discovery                     ClusterIP      None            <none>                                   9300/TCP                                                     17h
graylog-opensearch-cluster-masters                       ClusterIP      None            <none>                                   9200/TCP,9300/TCP                                            17h
graylog-opensearch-cluster-nodes                         ClusterIP      None            <none>                                   9200/TCP,9300/TCP                                            17h
mdb0-svc                                                 ClusterIP      None            <none>                                   27017/TCP                                                    20h
opensearch-operator-controller-manager-metrics-service   ClusterIP      10.109.239.13   <none>                                   8443/TCP                                                     22h
```



Розгортання HAPROXY
https://github.com/haproxytech/helm-charts
Додаємо репозиторій

```
helm repo add haproxytech https://haproxytech.github.io/helm-charts
helm repo update
```


А далі шукаємо доступні версії
`helm search repo haproxytech/`


```
helm search repo haproxytech/
NAME                            CHART VERSION   APP VERSION     DESCRIPTION
haproxytech/haproxy             1.19.3          2.8.2           A Helm chart for HAProxy on Kubernetes
haproxytech/kubernetes-ingress  1.33.0          1.10.7          A Helm chart for HAProxy Kubernetes
```
 Ingress Con...

INSTALL: type deamonset use all nodes to recive traffic and useHostPort 

`helm install haproxy haproxytech/kubernetes-ingress -n graylog --set controller.kind=DaemonSet --set controller.daemonset.useHostPort=true`

setup ingress:
Далі розгортаємо контроллер з опису
`kubectl apply -f graylog/ingress-graylog.yaml`
