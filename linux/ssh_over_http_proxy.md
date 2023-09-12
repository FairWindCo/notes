# Linux
Для того щоб отримати доступ до серверу SSH через проксі треба зробити налаштування,
або в файл
/etc/ssh/ssh_config
для всіх користувачів, або в файл користувача ~/.ssh/config

І тут є кілька варіантів:
або загальне налаштування в форматі
```
ProxyCommand nc -X connect -x fw02.bs.local.erc:8080 %h %p
```
Або ось такого типу: (не пробував)
```
Host *
  ProxyCommand corkscrew example-proxy.com 8080 %h %p ~/.ssh/proxyauth
```
Або під конкретний хост
```
Host github.com
  PreferredAuthentications publickey
  IdentityFile ~/keys/github_private
  ProxyCommand connect -H fw02.bs.local.erc:8080 %h %p
  ForwardAgent yes

Host remotehost
    hostname 192.168.1.10
    user remoteuser
    ProxyCommand nc -X4 -x 127.0.0.1:2222 %h %p
```
> ssh remotehost

За замовчуванням connect - немає,  треба його встановити `apt install connect-proxy`
Або використовувати команду nc

В деяких Алпін дистрибутивах немає підтримки проксі в nc, тоді требе встановити:
`apk add netcat-openbsd --no-cache`

Є також додаткові опції
`ServerAliveInterval   10`

# ДЛЯ ДОКЕРУ
## Для dockerfile
```
ENV http_proxy 'http://user:pass@10.78.2.60:9090'
ENV https_proxy 'http://user:pass@10.78.2.60:9090'
```
## Для глобальних налаштувань в конфіг
```
Host github.com
  PreferredAuthentications publickey
  IdentityFile /etc/ssh/github_private
  ProxyCommand nc -X connect -x fw02.bs.local.erc:8080 %h %p
```

# ДЛЯ GIT:
### Method 1. git http + proxy http
git config --global http.proxy "http://127.0.0.1:1080"
git config --global https.proxy "http://127.0.0.1:1080"

### Method 2. git http + proxy shocks
git config --global http.proxy "socks5://127.0.0.1:1080"
git config --global https.proxy "socks5://127.0.0.1:1080"

### to unset
git config --global --unset http.proxy
git config --global --unset https.proxy

### Method 3. git ssh + proxy http
vim ~/.ssh/config
```
Host github.com
HostName github.com
User git
ProxyCommand socat - PROXY:127.0.0.1:%h:%p,proxyport=1087
```
### Method 4. git ssh + proxy socks
vim ~/.ssh/config
```
Host github.com
HostName github.com
User git
ProxyCommand nc -v -x 127.0.0.1:1080 %h %p
```
------------------------------------------------------------------------------------------
# Використання SSH як проксі
### [step 1] create a ssh-proxy
  ssh -D 9999 -qCN user@server.net

### [step 2] make git connect through the ssh-proxy
  ### [current script only]
>   export GIT_SSH_COMMAND='ssh -o ProxyCommand="connect -S 127.0.0.1:9999 %h %p"'
  ### OR [git global setting] 
>  git config --global core.sshCommand 'ssh -o ProxyCommand="connect -S 127.0.0.1:9999 %h %p"'
  ### OR [one-time only use]
>  git clone -c=core.sshCommand 'ssh -o ProxyCommand="connect -S 127.0.0.1:9999 %h %p"' git@github.com:user/repo.git
  ### OR [current repository use only]
>  git config core.sshCommand 'ssh -o ProxyCommand="connect -S 127.0.0.1:9999 %h %p"'




# В операційній системі Windows
C:\Users\username\.ssh\config:
```
Host otherside
    HostName example.com
    User torvalds
    Port 443
    IdentityFile C:\Users\torvalds\.ssh\id_ed25519
    ProxyCommand C:\Program Files (x86)\Nmap\ncat.exe --proxy 10.20.30.40:8080 %h %p
    LocalForward 9999 127.0.0.1:5050
```
