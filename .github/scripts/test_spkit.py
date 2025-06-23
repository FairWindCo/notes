import re

input_data = """
commit 0fd5b2f97a57d25de63f0c8becad659d5b248df1
Author: skir <iliaskirko@gmail.com>
Date:   Thu Jun 5 08:57:10 2025 +0300

    acutalized config fields

diff --git a/Setting-up-device-uk.md b/Setting-up-device-uk.md
index 6d2649b..d494873 100644
--- a/Setting-up-device-uk.md
+++ b/Setting-up-device-uk.md
@@ -88,7 +88,8 @@ Password: `integrator`
                 "autostart_enabled": true,
                 "service_name": "video",
                 "rtp_receiver_port": 51746,
-                "radio_port": 1
+                "radio_port": 1,
+                "params_receiver_address": "127.0.0.1:5001"
             }
         },
         {
@@ -106,15 +107,19 @@ Password: `integrator`
                 "autostart_enabled": false,
                 "service_name": "video1",
                 "rtp_receiver_port": 51748,
-                "radio_port": 2
+                "radio_port": 2,
+                "params_receiver_address": "127.0.0.1:5002"
             }
         }
     ],
     "ser2net": {
         "connections": [
-            "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550",
-            "udp,127.0.0.1,5761:raw:600:/dev/ttyACM0:57600 remaddr=udp,127.0.0.1,14550"
+            "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550"
         ]
+    },
+    "frequency_filter": {
+        "enabled": true,
+        "ranges": [[2505,2580,5],[2603,2607,5]]
     }
 }

@@ -144,10 +149,14 @@ Password: `integrator`
   - `video_sender`: `object`. Налаштування для сервісу який відповідає за отримання RTP пакетів та пересилку їх по радіо.
     - `autostart_enabled`: `true`/`false` - `bool`. Увімкнути або вимкнути автозапуск передачі відео з запуском модему.
     - `rtp_receiver_port`: `int`. Порт на якому отримувати RTP пакети з джерела відео, повинен бути унікальним.
-    - `service_name`: `string`. Назва `procd` скрипту для запуску відео сервісу.
+    - `service_name`: `string`. Назва `procd` скрипту для запуску відео сервісу, може бути `video` або `video1`.
     - `radio_port`: `int`. Id радіо порту куди посилати відео.
+    - `params_receiver_address`: `ip:port` - `string`. Адреса для конфігурування.
 - `ser2net`: `object`. Налаштування для Set2Net.
   `connections`: `array[string]`. Масив `connection setting`, будь ласка зверніться до інструкції по Ser2Net.
+- `frequency_filter`: `object`. Налаштування відображення списку доступних частот на інтерфейсі користувача.
+  - `enabled`: `true`/`false` - `bool`. Позначити як увімкнений або вимкнений.
+  - `ranges`: `array[array[int]]`. Список діапазонів дозволених частот. Кожен діапазон задається трьома числами: `[початкова частота діапазону, кінцева частота, крок частот в діапазоні]`. Список для інтерфейсу заповнюється наступним чином: `початкова частота` включена в діапазон, потім в список додаються частоти з `кроком`, поки значення не більше за `кінцеву частоту`.

 ### **Налаштування наземної станції**

@@ -175,7 +184,8 @@ Password: `integrator`
     "video_channels": [
         {
             "channel_id": 0,
-            "channel_name" : "camera0",
+            "channel_name" : "camera0",,
+            "streams": ["Main"]
             "video_receiver": {
                 "service_name": "video",
                 "radio_port": 1,
@@ -184,7 +194,8 @@ Password: `integrator`
         },
         {
             "channel_id": 1,
-            "channel_name" : "camera1",
+            "channel_name" : "camera1",,
+            "streams": ["Main"]
             "video_receiver": {
                 "service_name": "video1",
                 "radio_port": 2,
@@ -197,9 +208,12 @@ Password: `integrator`
     },
     "ser2net": {
         "connections": [
-            "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550",
-            "udp,127.0.0.1,5761:raw:600:/dev/ttyACM0:57600 remaddr=udp,127.0.0.1,14550"
+            "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550"
         ]
+    },
+    "frequency_filter": {
+        "enabled": true,
+        "ranges": [[2505,2580,5],[2603,2607,5]]
     }
 }
 ```
@@ -216,14 +230,18 @@ Password: `integrator`
   - `enabled`: `true`/`false` - `bool`. Позначити як увімкнений або вимкнений.
   - `transport`: `mavlink` / `skyline`. Протокол передачі повідомлень MAVLink або Skyline DVS.
   - `to_address`: `ip:port`. IP адреса та порт модему телеметрії на наземній станції, або підключення Ser2Net.
+  - `streams`: `array[string]`. Масив назв для потоків відео на дроні. Порядок та кількість повинні відповідати порядку і кількості відео потоків на дроні.
 - `video_channels`: масив відео каналів.
   - `channel_id`: `int`. Унікальний ідентифікатор каналу.
   - `channel_name`: `string`. Імʼя каналу для користувача.
   - `video_receiver`: `object`. Налаштування для сервісу який відповідає за отримання пакетів відео по радіо і передачу їх на компʼютер оператора.
-    - `service_name`: `string`. Назва `procd` скрипту для запуску сервісу.
+    - `service_name`: `string`. Назва `procd` скрипту для запуску сервісу, може бути `video` або `video1`.
     - `radio_port`: `int`. Id  порту на якому отримувати відео.
     - `stream_to_address`: `ip:port`. IP адреса компʼютеру оператора, і порт який використовується в `gstreamer` для отримання відео пакетів.
 - `rssi_receiver`: `object`. Налаштування для локального веб-сервера який відповідає за читання значень RSSI с сервісу передачі відео.
   - `local_address`: `ip:port` - `string`. Порт повинен бути унікальним.
 - `ser2net`: `object`. Налаштування для Set2Net.
   `connections`: `array[string]`. Масив `connection setting`, будь ласка зверніться до інструкції по Ser2Net.
+- `frequency_filter`: `object`. Налаштування відображення списку доступних частот на інтерфейсі користувача.
+  - `enabled`: `true`/`false` - `bool`. Позначити як увімкнений або вимкнений.
+  - `ranges`: `array[array[int]]`. Список діапазонів дозволених частот. Кожен діапазон задається трьома числами: `[початкова частота діапазону, кінцева частота, крок частот в діапазоні]`. Список для інтерфейсу заповнюється наступним чином: `початкова частота` включена в діапазон, потім в список додаються частоти з `кроком`, поки значення не більше за `кінцеву частоту`.
diff --git a/Setting-up-device.md b/Setting-up-device.md
index 47ebfcd..646c288 100644
--- a/Setting-up-device.md
+++ b/Setting-up-device.md
@@ -97,6 +97,10 @@ Or by editing `/tltk_state/config.json` config file (accessible by `root` user).
             "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550",
             "udp,127.0.0.1,5761:raw:600:/dev/ttyACM0:57600 remaddr=udp,127.0.0.1,14550"
         ]
+    },
+    "frequency_filter": {
+        "enabled": true,
+        "ranges": [[2505,2580,5],[2603,2607,5]]
     }
 }

@@ -130,6 +134,9 @@ Or by editing `/tltk_state/config.json` config file (accessible by `root` user).
     - `radio_port`: `int`. Port id to where to send video.
 - `ser2net`: `object`. Settings for Set2Net.
   `connections`: `array[string]`. Array of connection settings, please refer to Ser2Net manual.
+- `frequency_filter`: `object`. Settings for displaying a list of allowed frequencies in user interface.
+  - `enabled`: `true`/`false` - `bool`. Mark enabled or disabled.
+  - `ranges`: `array[array[int]]`. The list of allowed frequency ranges. Each range is defined by three numbers: `[start frequency, end frequency, step]`. A range is populated this way: the `start frequency` is included in the range, then more frequencies added by adding a `step`, until the value to be added in the range is not greater than the `end frequency`.

 ### **GS configuration**

@@ -182,6 +189,10 @@ Or by editing `/tltk_state/config.json` config file (accessible by `root` user).
             "udp,127.0.0.1,5761:raw:600:/dev/ttyUSB0:57600 remaddr=udp,127.0.0.1,14550",
             "udp,127.0.0.1,5761:raw:600:/dev/ttyACM0:57600 remaddr=udp,127.0.0.1,14550"
         ]
+    },
+    "frequency_filter": {
+        "enabled": true,
+        "ranges": [[2505,2580,5],[2603,2607,5]]
     }
 }
 ```
@@ -209,6 +220,9 @@ Or by editing `/tltk_state/config.json` config file (accessible by `root` user).
   - `local_address`: `ip:port` - `string`. Port must not conflict with ports in other settins.
 - `ser2net`: `object`. Settings for Set2Net.
   `connections`: `array[string]`. Array of connection settings, please refer to Ser2Net manual.
+- `frequency_filter`: `object`. Settings for displaying a list of allowed frequencies in user interface.
+  - `enabled`: `true`/`false` - `bool`. Mark enabled or disabled.
+  - `ranges`: `array[array[int]]`. The list of allowed frequency ranges. Each range is defined by three numbers: `[start frequency, end frequency, step]`. A range is populated this way: the `start frequency` is included in the range, then more frequencies added by adding a `step`, until the value to be added in the range is not greater than the `end frequency`.

 ## V2 pinout
 <p align="center">

"""

commits_raw = re.split(r'(?=^commit\s)', input_data, flags=re.MULTILINE)
commits_raw = commits_raw[:1]
print(commits_raw)