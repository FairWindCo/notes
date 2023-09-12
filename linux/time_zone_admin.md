# Часова зона та синхронізація часу
## Перевірка поточного стану
Контроль часу команда: `timedatectl`

За замовчуванням таймзона має вигляд:

```
timedatectl

               Local time: пн 2023-09-11 11:48:05 UTC
           Universal time: пн 2023-09-11 11:48:05 UTC
                 RTC time: пн 2023-09-11 11:48:06
                Time zone: Etc/UTC (UTC, +0000)
System clock synchronized: no
              NTP service: active
          RTC in local TZ: no
```
Тут бачимо "*System clock synchronized: no*", що значить що синхронізації немає,
крім того часова зона Etc/UTC (UTC, +0000)

## Встановити часову зону та синхронізацію
Для цього встановити часову зону:

`timedatectl set-timezone Europe/Kiev`

змінити файл  vi /etc/systemd/timesyncd.conf

Наступні зміни:
```
[Time]
NTP=dcbs0101.bs.local.erc
FallbackNTP=dcbs0201.bs.local.erc
#RootDistanceMaxSec=5
PollIntervalMinSec=32
PollIntervalMaxSec=2048
```
Вімкнути сихронізацію
`timedatectl set-ntp on`

Переазпустити демона
`systemctl restart systemd-timesyncd.service`

Перевірити роботу:
```
timedatectl
               Local time: пн 2023-09-11 12:55:23 EEST
           Universal time: пн 2023-09-11 09:55:23 UTC
                 RTC time: пн 2023-09-11 09:55:23
                Time zone: Europe/Kiev (EEST, +0300)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

Тепер бачимо ключьові значення:

> Time zone: Europe/Kiev (EEST, +0300)
> 
> System clock synchronized: yes
> 
> NTP service: active
               
Що значать, зона Europe/Kiev, час сихронізовано, агент часу активний

