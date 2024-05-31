# Вказати дані для підлючення до cifs
Створюємо файли з паролями, наприклад так:
```
sudo nano /etc/.smbcredentials1
sudo nano /etc/.smbcredentials2
sudo nano /etc/.smbcredentials3
```
Заповнюємо в такому вигляді
```
username=your_shared_linx_and_qnap_username
password=the_qnap_user_password_you_chose
domain=WORKGROUP
```
Задаємо права доступу (дуже важливо)
```
sudo chmod 0600 .smbcredentials1 .smbcredentials2 .smbcredentials3 
```
Заповнюємо файл fstab
```
//server/share /mount/point cifs ro,auto,credentials=/etc/.smbcredentials1 0 0
//server/share /mount/point cifs ro,auto,credentials=/etc/.smbcredentials2 0 0
//server/share /mount/point cifs ro,auto,credentials=/etc/.smbcredentials3 0 0
```
Більш узагальнений варінт запису в fstab
```
//[URL]/[sharename] /media/[mountpoint] cifs vers=3.0,credentials=/home/[username]/.sharelogin,iocharset=utf8,file_mode=0777,dir_mode=0777,uid=[username],gid=[username],nofail 0 0
```
[https://askubuntu.com/questions/1119819/how-do-i-use-a-credential-file-for-cifs-in-etc-fstab]
