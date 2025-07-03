<style>
r { color: Red }
o { color: Orange }
g { color: Green }
</style>

# Terraform
Це інструмент, що дозволяє зробити опис інфраструктури, а потім привести вказану інфрастурктуру у стан, що був заданий описом.
Важливим моментом, варто зазаначити, що терраформ працює лише в одному напрямку, тобто неможливо вже існуючи конфігурацію перетворити в опис.
Це важливо в тому випадку, що якщо ви внесете зміни вручну і потім застосуєте конфігурацію то ваші зміни будуть знищені.

Сам Terraform являє собою фактично один єдиний бінарний файл написаний на ГО, а також окремо сам терраформ може скачати провайдери для конкретних хмарних платформ, що теж являють собою бінарні файли (проте достатньо виликих ромірів).
Конфігурація описується в текстовому файлі (заведено давати файлам розширення tf).

Сам тераформ можна звантажити за посиланням: https://developer.hashicorp.com/terraform/install
Сам тераформ має вилику кількість провайерів для работи з хмарними інфраструктурами.
Встановлення досить просте завантажити архів та разпакувати, потім або дадати змінну PATH що б вона вказувала на каталог де лежить файл, або покласти файл в такий каталог яка вже є в PATH

Документацію для провайдера AWS шукаємо тут: https://registry.terraform.io/providers/hashicorp/aws/latest/docs


## <g>Конфігурації</g>
Напочатку файл конфігурації єде опис необхдних провайдерів, що відповідають за те на яких платформах буде створюватися інфраструктура.
Наприклад для підключення провайдера для aws, необхідно на початок додати такий код:
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.81.0"
    }
  }
}
```
Тепер, для того, щоб працювати з платформою необхідно встановити необхідного провайдера, для цього виконують команду:
`terraform init`

Для того, щоб підключатися до платформи необхіно вказати дані для аутентіфікації, це робиться таким чином:
```
provider "aws" {
access_key = "KEY"
secret_key = "SECRET"
region     = "REGION"
}
```
Вказуються дані для створеного користувача, а також регіон де виконується сервіси.
Потім йде опис секрвісів, що повинні створитися:
```
resource "aws_instance" "test_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
```
Це опис створює віртуальну машину з назвою test_machine, для ОС використовуєтсья ami-03250b0e01c28d196 (що відповідає за Убунту, їх перелік можна дізнатися зі сторінки де в консолі админістратора створюється новий інстанс)
Крім того, використовується шаблон ресурсів: t3.micro.

## Застосування конфігурації
Розлянено дві наступні команди:
- `terraform plan`
- `terraform apply`

Перша показує, що саме збирається зробити тераформ, спочатку він з1єдається з платформою дізнається що там на справді є потім порівняє зі збереженим станом (що зберігається в файлі з розширенням tfstate) а потім з конфігурацією і якщо він виявить розбіжності то сформує план їх усунення.
Друга команда безпосередньо застосовує зміни (і хоча перша команда не є необхідною для важливих конфігурацій краще спершу застосовувати її та перевіряти ті дії які будуть виконані).
<r>Важливо після виконання apply буде створено tfstate (формат JSON) в якому зеберуться всі параметри того, що було створено, а головне їх ідентифікатори. Якщо цей файл видалити, то тераформ буде вважати, що нічього не створено і буде створювати все заново, а керування тім що було буде встрачено.</r>
При виконанні apply, тераформ перевіряє наявність tfstate, якщо він є - то буде йти порівняння з тим, що вже є, якщо файла немає, то просто йде створення нових ресурсів.

Для того, щоб змінити конфіграцію треба внести в файл необхідні зміни та застосувати її. (якщо з файлу щосу було видално, то воно видалеться і з хмари, те саме зі змінами та додаванням.)
Варто зазаначити, що часто зміна це не редагування на літу, в кращому випадку відбудеться запинення ресурсу, його зміна, а потім запуск, що займе певний час. Проте в деяких випадках буде не зміна ресурсу а його видалення та створення нового, що варто враховувати.

Для видалення всього якщо конфігурація необхідна:
`terraform destroy`
видалить повністю всі ресурси що є в стані. Наприклад для цілей провести роботу, а потім її зупинити.

Не варто зберігати ключи безпосередньо в конфігурації, краще, наприклад прописувати їх як змінні сесії:
```
export AWS_ACCESS_KEY_ID=<id>
export AWS_SECRET_ACCESS_KEY=<secret>
export AWS_DEFAULT_REGION=eu-central-1
```
# Зміна конфігурації
В разі, якщо потрібно внести зміни в конфігурацію, просто потрібно відредагувати наш текстовий опис конфігурації (файл .tf). Потім викликається команда: `terraform apply` (хоча перед нею варто викликати команду plan, щоб перевірити заплановані дії).
В разі коли сервіс зможе внести зміни в конфігурацію від змінить поточний ресурс, проте деякі операції не можут бути виконаним на робочьому сервіси, тоді тераформ знищить що існує ресурс та створить новий. Варто відзначити, що редагування буде ймовірніше виконуватися коли ресурс в стані - зупинено. 
Тому тераформ спочатку зупинить ресурс внисе зміни та знову запустить. 
Параметри які можна змінити\або задати при створенні для інстансу можна подивитися в документації за посиланням: https://registry.terraform.io/providers/hashicorp/aws/3.6.0/docs/resources/instance

Наприклад для ресурсу можна задати теги:
```
resource "aws_instance" "web" {
  ami           = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"

  tags = {
    Name = "HelloWorld"
  }
}
```
Цей тег буде відображатися в колонках в назві ресурсу в консолі aws.
Ще один цікавий параметр це count, за замовчуванням має значення 1. Проте можна вказати більше тоді, тераформ автоматично створить необхідну кількість екземплярів.
Також слід розуміти, що якщо вручну внести зміни в хмару, або вносити зміни в файл опису, то тераформ приведе все до стану як вказано в файлі в все зайве видалить.
Якщо, наприклад, з опису видалити тегі, то тераформ зробить так само в хмарі.
Але є певна особливість того, що він не створював він чепати не буде. Тобто якщо є ресурси створені за межами тераформа, то він їх не бачить і не буде їх, а не змінювати, а ні видяляти.
Тому дуже важливо зберігати файл стану тераформу tfstate, бо якщо його видалити тераформ забуде про те, що він створив і ствоить нові ресурси, а старі будуть вже не керованими. Далі управління ними тільки вручну через консоль.
# Видалення русурсів
Є команда 'terraform destroy', яка видаляє все що було створено. Фактично можна підняти ресурси відпрцювати необхідну роботу, а потім все видалити.

# Приклад простого сервіса
В якості, прикладу, розгорнемо WEB сервіс: для цього створемо наступний опис:
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.81.0"
    }
  }
}
provider "aws" {
  region     = "eu-central-1"
}
resource "aws_instance" "test_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.my-sec-web.id]
  user_data = <<EOF
#!/bin/bash
apt update
apt upgrade
apt -y install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
EOF
  
  tags = {
    Name = "Web Server"
  }
  }

resource "aws_security_group" "my-sec-web" {
  name = "my-security-web-rule"
  ingress {
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    cidr_blocks       = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 65535
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Security Policy for web server"
  }
}
```
В цьому описі творюється один ресурс "test_machine" та одна група безпеки "my-sec-web", що описує дозволи на вхідний "ingress" та вихідний "egress" трафік. В прикладі відкрито один порт 443 протокол tcp для вхідного трафіку з будь-яких хостів `cidr_blocks = ["0.0.0.0/0"]` та будь-який вихідний трафік (всі порти, всі протоколи та на всі хости). Хоча тут можна задавати певні обмеження.
Також в цьому прикладі заданий скрипт, що виконується при створенні ресурсу, вказується параметром user_data:
```
  user_data = <<EOF
#!/bin/bash
apt update
apt upgrade
apt -y install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
EOF
```
Фактично при створенні виконаються всі ці команди одна за одною. Для ресурсів AWS user_data виконується лише один раз при створенні ресурсу та не можу бути змінена (лише шляхом перестворення ресурсу).
Також в приладі одразу прописані тегі, що довзоляють красиво бачити імена ресурсів в консолі AWS, бо імена задані параметрами name, використовуються як внутрішні імена тераформа. Тому, ті що будуть в консолі повинні бути задані через тегі.
Такий підхід можна використати, якщо скрипт запуску не великий, проте можна зробити по іншому винести скрипт у зовнішній статичний файл.

## Статичний файл 

Якщо винести скрипт у файл, наприклад "init_script.sh", наступного змісту:
```
#!/bin/bash
apt update
apt upgrade
apt -y install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```
Тоді його можна включити таким чином:
```
user_data = file("init_script.sh")
```
Тоді замість коду скрипту в описі, він виноситься в окремий файл, який включається через функцію `file`. Це дозволяє спростити опис, крім того, дає можливість повторного використання скриптів, ті їх роздільної розробки.
Проте іноді такий файл потрібно параметрезувати даними від самого тераформ, це можна зробити через шаблони.

## Динамічний шаблон

Також в окремих випадках потрібно передати деякі змінні чи ідентифікатори свередину скрипту. В нашому випадку ми зробемо сторінку для web серверу прямо в скрипті:
Для цього створемо новий файл "init.tpl", такого змісту:
```
#!/bin/bash
apt update
apt upgrade
apt -y install nginx
sudo systemctl enable nginx
sudo systemctl start nginx

echo <<EOF > /var/www/html/index.html
<html>
<h2>${my_variable}</h2>
<ul>
%{~ for x in my_list_var ~}
    <li>${x}</li>  
%{~ endfor ~}
</ul>
</html>
EOF
```
Крім стандартних команд можна побачити блок всередині якого використовуються змінні. Наприклад виводиться змінна "my_variable".
Також тут є можливість використання циклів (блок зі змінною my_list_var).
Підключається до опису через виклик функції templatefile, на першому місці задається шлях до файлу шаблона, другий параметр це словник з даними що передаються всередину скрипту (ключ це назва змінної всередині шаблона).
```
user_data = templatefile("init.tpl", {
   "my_variable" = "test",
   "my_list_var" = ["test1", "test 2", "test n"]
 }) 
```
Крім значень заданих заздалегідь, можна використати значення з тераформу.

Є можливість перевірити роботу функцій через команду: `terraform console`, можна зайти в консоль і тут можна напряму випробувати функції. Наприклад: `file("init.sh")` - видасть зміст файла.
А команда `templatefile("init.tpl", {"my_variable" = "test","my_list_var" = ["test1", "test 2", "test n"]})` - видасть зміст файлу, але з застосованими змінними. 

# Динамічні блоки
Іноді в описах ресурсів потрібно застосовувати типові блоки, що повторюються, які можна замінити через автоматичне генерування. Наприклад для політики, якщо потрібно відкрити кілька портів її можна задати таким чином:
```
resource "aws_security_group" "my-sec-web" {
  name = "my-security-web-rule"
  dynamic "ingress" {
    for_each = ["8080", "8081"]
    content {
        from_port         = ingress.value
        to_port           = ingress.value
        protocol          = "tcp"
        cidr_blocks       = ["0.0.0.0/0"]       
    }
  }
  
  ingress {
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    cidr_blocks       = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 65535
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Security Policy for web server"
  }
}
```
В цій политиці є частина статична, що не змінюється та не залежить від параметрів, а є частина "dynamic", що генерується для кожного значення з "for_each", використовуючи "content".
В цьому випадку, використання ще одного статичного "ingress" чи "egress" - не є обов'язковим, блок міг би бути повністю динамічним.
Динамічні блоки працють від версії 0.12.

## LifeCycle ресурсів
Для ресурсів можна задати кілька параметрів, що відповідають за процеси які відбуваються з ресурсом, а саме:
```
resource "aws_instance" "test_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
  
  ........
  
    lifecycle {
    prevent_destroy = true  
    ignore_changes = ["ami", "user_data"]
    create_before_destroy = true
  }
}
```
prevent_destroy - забороняє видалення ресурсів. Якщо якісь зміни будуть потребувати видалення ресурсів, то вони будуть заблоковані та не виконаються. Наприклад для розгорнутих БД, що не втрати дані.
ignore_changes - вказує зміни яких параметрів не повинні привезти змін ресурсу, вказуються як список. Всі зміни цих параметрів будуь проігноровані. Іноді це використовуються для того, щоб не дати перестворити ресурс.
create_before_destroy - вказує тераформ, спочатку створити новий ресурс на заміну старому, а потім видалити старий, таким чином зменшується час простою.

**Примітка**: 
Ось приклад коду, що створює статичний ІР та прив'язує його до інстансу:
```
resource "aws_eip" "my_static_ip" {
 instance = aws_instance.test_machine.id
}
resource "aws_instance" "test_machine" {
......
}
```
Відмітимо кілька моментів, перший і він стосується всього тераформ, тут можна ссилатися на елементи по типу aws_instance.test_machine.id, де aws_instance - тип ресурсу,  test_machine - ім'я ресурсу всередині тераформ конфігу (не плутати з іменем в хмарі, це інше), а далі конкретний атрибут для посилання. В нашому випадку це атрибут ID, що означає унікальний ідентифікатор об'єкту в хмарі.
Цей фрагмент створить статичну ІР адресу та прив'яжа його до вказаного інстансу (код якого приведено скорочено).

# Вивід атрибутів
Система тараформ дозволяє виводити корисну інформацію про ресурси, що створюються в консоль.
Для цього всередину опису тераформ розміщуються блоки `output` за обов'язковими призначеннями їх назви "назва_output" та визначення їх значення у вигляді посилання на атрибут ресурсу.
```
resource "aws_eip" "my_static_ip" {
 instance = aws_instance.test_machine.id
}
resource "aws_instance" "test_machine" {
......
}
output "test_machine_instance_id" {
  value = aws_instance.test_machine.id
}
output "test_machine_public_ip" {
  value = aws_instance.my_static_ip.public_ip
  description = "опис виводу, фактично як коментар"
}
```
При виконанні такого опису, в кінці після повідомлення про успішні зміни буде виведено блоки output у вигляді пар значень "назва та значення" для нашого прикладу це test_machine_instance_id="значення aws_instance.test_machine.id"
Друге значення output відобразить public_ip.
Є спеціалізована команда тераформ `terraform output` - вона лише відобразить значення блоків output. Проте тут є нюанс, що вона відобразить лише ті значення блоків, що існували під час команди apply. Кажучи іншими словами, не можливо створити ресурс, а потім додати окремо блоки виводу. Все одно потрібно буде спочатку зробити apply, а лише потім для них буде доступним output.
Також блоки output можуть бути використовуватися для з'єднання кількох тераформ описів. Значення description для блоків output, задається для поліпшення читання та ніде не відображаються.
Для виводу інформації про об'єти та їх атрібути можна скористатися командою `terraform show`, ця команда читає файл tfstate та форматовано відображає його значення, таким чином можна побачити створені ресурси та їх атрибути.
Загальна рекомендація: всі важливі значення, як то ідентифікатори, виводи за допомогою output. Кажучи простіше багато output це корисно. Крім того, бажано output виносити в окремий файл з назвою "output.tf".

**ВАЖЛИВО**: тераформ аналізує всі файли в директорії в який він запускається. Фактично він об'єднує всі файли в один в па'яті, а потім аналізує все разом. Тому немає важливості який порядок.
Часто змінні виносять в файли "variable.tf", основний код в "main.tf".

# Порядок створення ресурсів
Припустимо нам потрібно створити кілька серверів, опис міг би мати такий вигляд:
```
resource "aws_instance" "test_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
}
resource "aws_instance" "api_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
}
resource "aws_instance" "db_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
}
```
Проте такий опис значить, що всі ці три ресурси будуть створюватися одночасно. Проте в певних випадках це не може бути корисним, бо сервіси можуть мати залежності один він одного. Для цього інсує атрибут "depends_on", що являэ собою список ресурсів які повинні існувати на момент створення ресурсу.
Тоді опис матиме вигляд такий:
```
resource "aws_instance" "test_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
  depends_on = [aws_instance.db_server_machine,aws_instance.api_server_machine]
}
resource "aws_instance" "api_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
  depends_on = [aws_instance.db_server_machine]
}
resource "aws_instance" "db_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t3.micro"
}
```
Тут вказані явні залежності одних ресурсів від інших. Параметр depends_on працює не лише при створенні ресурсів, а і при виконанні зворотної операції видалення, вони також будуть видалятися в порядку зворотному створенню.
Проте головне уникати циклічних посилань.

## Отримання даних за допомогою Data Source
Опис документації: https://developer.hashicorp.com/terraform/language/data-sources
AWS data source: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/instances
Data Source дозволяє тераформ використовувати інформацію, що створена за межами тераформ або в інших тераформ.

Наприклад таким постачальником даних може бути aws_availability_zones:
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones
В базовому вигляді створюємо ось такий опис:
```
data "aws_availability_zones" "available" {}
```
Тепер в своємо коді ми може їх застосувати, наприклад вивезти на екран:
```
data "aws_availability_zones" "available" {}
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

output "available_names" {
  value = data.aws_availability_zones.available.names
}
output "available_name_1" {
  value = data.aws_availability_zones.available.names[0]
}
output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
output "caller_arn" {
  value = data.aws_caller_identity.current.arn
}
output "caller_user" {
  value = data.aws_caller_identity.current.user_id
}
output "region_name" {
  value = data.aws_region.current.name
}
output "region_desc" {
  value = data.aws_region.current.description
}
```
Такий опис, якщо його застосувати нічього не створить всередині хмари, проте виведе значення типу:
```
account_id = "<account id>"
available_name_1 = "eu-central-1a"
available_names = tolist([
  "eu-central-1a",
  "eu-central-1b",
  "eu-central-1c",
])
caller_arn = "arn:aws:iam::<number id>:user/<user name>"
caller_user = "<user caller>"
region_desc = "Europe (Frankfurt)"
region_name = "eu-central-1"
```
Тут вивело повний опис всіх aws_availability_zones, в змінну available_names, та першої зони (бо списки в тераформ рахуються від 0) в змінну available_name_1. Також блок даних aws_caller_identity дає інформацію про аккаунт.
Блок aws_region дає доступ до інформації про регіон.
Зазначемо, що якщо перейти по посиланню вище там можна найти розділ "Attribute Reference", де зазначені атрибути які існують, аналогічно такі описи є для всіх ресурсів.
Корісні
- VPC https://registry.terraform.io/providers/hashicorp/aws/3.9.0/docs/data-sources/vpc (тут наприклад можна отримати всі ідентифікатори вже ствоерних віртуалок)
Можливо застосовувати фільтри до пошуку необхідної інформації:
```
data "aws_vpc" "product_vpc" {
  tags = {
     Name = "product_web_server"
  }
}
```
Цей датасет знайде всі віртуальні машини vpc та вибери з них ті в яких існує тег Name зі значенням "product_web_server", іншими словами це буде віртуальна машина з іменем "product_web_server".
Розглянемо приклад, нам потрібно до вже існуючьої віртуальної машини створити мережі:
```
data "aws_availability_zones" "available" {}
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_vpc" "product_vpc" {
  tags = {
     Name = "product_web_server"
  }
}

resource "aws_subnet" "prod_subnet_1" {
   vpc_id = data.aws_vpc.product_vpc.id
   availability_zone = data.aws_availability_zones.available.names[0]
   cidr_block = "10.10.10.0/24"
   tags = {
     Name = "Subnet - 1 in ${data.aws_availability_zones.available.names[0]}"
     Account = "Account ${data.aws_caller_identity.current.account_id}"
     Region = data.aws_region.current.description
   }  
}

resource "aws_subnet" "prod_subnet_2" {
   vpc_id = data.aws_vpc.product_vpc.id
   availability_zone = data.aws_availability_zones.available.names[2]
   cidr_block = "10.20.10.0/24"
   tags = {
     Name = "Subnet - 2 in ${data.aws_availability_zones.available.names[2]}"
     Account = "Account ${data.aws_caller_identity.current.account_id}"
     Region = data.aws_region.current.description
   }  
}

output "prod_id" {
  value = data.aws_vpc.product_vpc.id
}
output "prod_cidr_block" {
  value = data.aws_vpc.product_vpc.cidr_block
}
```
Фактично цей опис створить дві мережі, саме цікаве тут це використання значень для ствоерння ресурсів без необхідності задавати їх руками.
Крім того, приклад демострує можливість використовувати значення в тестових строках (для тегів Name або Account).

## Автопошук AMI id за допомогою Data Source
За допомогою такого  Data Source можна автоматично знаходити ідентифікатори для образів ОС. Наприклад шукаємо убунту:
```
data "aws_ami" "latest_ubuntu" {
     owners = ["<акаунт ід власника образу>"]
     most_recent = true
     filter {
        name = "name"
        values = ["частина назви з зірочкою, або повна назва"]
     }
}
```
Для того, щоб дістати необхідні дані, йдемо в носоль AWS в розділ AMI, так шукаємо необхідний образ (з опису дістаємо власника, а для пошуку використовуємо ніобхідну частину назви):
Наприклад повний код для пошуку отснньої убунту:
```
data "aws_ami" "latest_ubuntu" {
     owners = ["099720109477"]
     most_recent = true
     filter {
        name = "name"
        values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
     }
}

output "latest_ami_id" {
  value = data.aws_ami.latest_ubuntu.id
}
output "latest_ami_name" {
  value = data.aws_ami.latest_ubuntu.name
}
```
Фактично цей пошук заходить в акаунт власника і шакає там по назві. Важливо, параметр most_recent вибирає останній, якщо його не вказати, то він знайде кілька штук і пошук впаде з помилкою, що знайдено більше одного. А тут завжди повинен бути один результат. Також приклад демонструю використання, в нашому випадку це вивід на екран, виведе щось типу:
```
latest_ami_id = "ami-02003f9f0fde924ea"
latest_ami_name = "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-20250610"
```
Приклад для пошуку амазон лінукс:
```
data "aws_ami" "latest_amason" {
     owners = ["137112412989"]
     most_recent = true
     filter {
        name = "name"
        values = ["amzn2-ami-hvm-*-arm64-gp2"]
     }
}
```
риклад для пошуку windows server 2025:
```
data "aws_ami" "latest_windows" {
     owners = ["801119661308"]
     most_recent = true
     filter {
        name = "name"
        values = ["Windows_Server-2025-English-Full-Base-*"]
     }
}
```
Приклад комплексного використання для створення ВЕБ серверу з автоматичноим скелінгом та лоад балансером: 
```
provider "aws" {
access_key = "KEY"
secret_key = "SECRET"
region     = "REGION"
}

data "aws_availability_zones" "available" {}
data "aws_ami" "latest_amason" {
     owners = ["137112412989"]
     most_recent = true
     filter {
        name = "name"
        values = ["amzn2-ami-hvm-*-arm64-gp2"]
     }
}
resource "aws_security_group" "my-sec-web" {
  name = "my-security-web-rule"
  dynamic "ingress" {
    for_each = ["80", "443"]
    content {
        from_port         = ingress.value
        to_port           = ingress.value
        protocol          = "tcp"
        cidr_blocks       = ["0.0.0.0/0"]       
    }
  }
  egress {
    from_port = 0
    to_port = 65535
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Security Policy for web server"
  }
}

resource "aws_launch_template" "web_server" {
  name = "Web_Server_LT"
  image_id = data.aws_ami.latest_amason.id
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.my-sec-web.id]

  user_data = filebase64("${path.module}/example.sh")
}

resource "aws_autoscaling_group" "my_ag" {
  name                      = "my autoscaling group"
  desired_capacity   = 1
  max_size           = 2
  min_size           = 2
  min_elb_capacity   = 2
  health_check_type         = "ELB"
  load_balancers = [aws_elb.web_elb.name]
  vpc_zone_identifier  = [aws_default_subnet.default_az2.id, aws_default_subnet.default_az1.id]
  
  launch_template {
    id      = aws_launch_template.web_server.id
    version = "$Latest"
  }  
  
  dynamic "tag" {
  for_each = {
     Name = "ASG web server"
     Owner = "My Company"
     TagName = "Tag Value"
  }  
  content {
      key                 = tag.key
      propagate_at_launch = true
      value               = tag.value
    }
  }
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_default_subnet" "default_az1" {
  availability_zone = data.aws_availability_zones.available.names[0]
}
resource "aws_default_subnet" "default_az2" {
  availability_zone = data.aws_availability_zones.available.names[1]
}

resource "aws_elb" "web_elb" {
  name               = "WebServer-elb"
  availability_zones = [data.aws_availability_zones.available.names[0],data.aws_availability_zones.available.names[1]]
  security_groups = [aws_security_group.my-sec-web.id]
  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }
}
output "web_dns_name" {
  value = aws_elb.web_elb.dns_name
}
    
```
Особливість амазона, що не можливо створити два ресурси з одним іменем, тому при внесенні змін в файл, його повторне застосування може призвести до помилки, тому що ресурс з таким іменем вже існує, а в нас вказано створити новий перед видаленням старого.
Рішенням цього є застосування параметра `name_prefix` замість `name`, тоді ми вказуємо частину імені обов'язкову, а далі тераформ сам щось додасть, щоб ім'я було унікальним.
Ще цікаве рішення, це створити залежність aws_autoscaling_group від aws_elb, щоб при зміні чогось в балансері створювалася нова група. Для цього змінено `name="my autoscaling group"` на `name="my ${aws_elb.web_elb.name}"`, тоді назва вже залежить від імені балансера, а при зміні балансера буде згенеровано нове ім'я.
При правильному використанні можна отримати систему, що працює без простоїв, якщо вносяться зміни, спочатку запустяться нові ноди, а потім зникають старі.
Ось посилання на документацію де описані ресурси, що застосовані:
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elb
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/default_subnet


Цікавіша історія це застосування green\blue deployment, нехай маємо такий скрипт даних (тут цікава url http://169.254.169.254/latest/meta-data/local-ipv4, що повертає локальну адресу ноди)
```
yum update
yum -y install httpd

myip = `curl http://169.254.169.254/latest/meta-data/local-ipv4
cat <<EOF > /var/www/html/index.html
<html>
<body>
MYIP: $myip <br>
Version: v1.0
</body>
</html>
EOF  
service httpd restart
chkconfig httpd on
```
Застосуємо тепер ALB (application Load Balancer)
```
provider "aws" {
access_key = "KEY"
secret_key = "SECRET"
region     = "REGION"
 default_tags {
  Owner = "Im"
  CreatedBy = "Terraform"
}
}

data "aws_availability_zones" "available" {}
data "aws_ami" "latest_amason" {
     owners = ["137112412989"]
     most_recent = true
     filter {
        name = "name"
        values = ["amzn2-ami-hvm-*-arm64-gp2"]
     }
}
resource "aws_default_vpc" "default" {}

resource "aws_default_subnet" "default_az1" {
  availability_zone = data.aws_availability_zones.available.names[0]
}
resource "aws_default_subnet" "default_az2" {
  availability_zone = data.aws_availability_zones.available.names[1]
}

resource "aws_security_group" "my-sec-web" {
  name = "my-security-web-rule"
  vpc_id = aws_default_vpc.default.id
  dynamic "ingress" {
    for_each = ["80", "443"]
    content {
        from_port         = ingress.value
        to_port           = ingress.value
        protocol          = "tcp"
        cidr_blocks       = ["0.0.0.0/0"]       
    }
  }
  egress {
    from_port = 0
    to_port = 65535
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Security Policy for web server"
  }
}

resource "aws_launch_template" "web_server" {
  name = "Web_Server_LT"
  image_id = data.aws_ami.latest_amason.id
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.my-sec-web.id]

  user_data = filebase64("${path.module}/example.sh")
}


resource "aws_autoscaling_group" "my_ag" {
  name                      = "WEB_Server_AG-${aws_launch_template.web_server.latest_version}"
  desired_capacity   = 1
  max_size           = 2
  min_size           = 2
  min_elb_capacity   = 2
  health_check_type         = "ELB"
  load_balancers = [aws_lb.web_lb.name]
  vpc_zone_identifier  = [aws_default_subnet.default_az2.id, aws_default_subnet.default_az1.id]
  target_group_arns = [aws_lb_target_group.web_target_g.arn]
  
  launch_template {
    id      = aws_launch_template.web_server.id
    version = "$Latest"
  }  
  
  dynamic "tag" {
  for_each = {
     Name = "ASG web server v${aws_launch_template.web_server.latest_version}"
     Owner = "My Company"
     TagName = "Tag Value"
  }  
  content {
      key                 = tag.key
      propagate_at_launch = true
      value               = tag.value
    }
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb" "web_lb" {
  name               = "WebServer-lb"
  load_balancer_type = "application"
  subnets             = [aws_default_subnet.default_az2.id, aws_default_subnet.default_az1.id]
  security_groups = [aws_security_group.my-sec-web.id]
}

resource "aws_lb_target_group" "web_target_g" {
  name     = "web-target"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_default_vpc.default.id
  deregistration_delay = 10
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.web_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_g.arn
  }
}

output "web_dns_name" {
  value = aws_lb.web_lb.dns_name
}
   
```
Приклад створює групу балансування, створює лоад балансер, групу для балансера, а також лістенара. Це більш нова версія такого плану функціоналу. Сервіси, створюються в групі маштабування та реєструються в таргет групі, далі якої працює балансер, що прослуховує порти задані в лістенері.
В цьому пркладі: default_tags - що задані для provider будуть застосовані для всіх ресурсів, що створені цим провайдером. Назва групи залежить від ${aws_launch_template.web_server.latest_version}, і тим самим при зміні версії темплейта, буде автоматично перестворено нову групу.
При цьому стара група буде знищена лише після того, як нова група стане повністю функціональна. Таким чином, наприклад якщо змінити скрпит запуску, то автоматично зміниться версія темплейта запсуку, що призведе для створення нової групи маштабування. Всі сервери коли вони піднімуться зарєєструються в таргет групі.
Параметр deregistration_delay, вказує на необхідність зачекати з видаленням старих серверів протягом вказаного часу (а не образу після того, як з'явиться новий сервер).

# Змінні
Гарної практики є винесення сього, що може бути змінено в окремі змінні для відділеня опису ресурсів від можливих змін. Наприклад:
```
variable "region" {
    description = "Enter region for deploy security group"
}

variable "cidr_block" {
    description = "Enter CIDR block address"
    type = string
    default = "0.0.0.0/0"
}
variable "open_ports" {
    description = "Enter ports"
    type = list
    default = ["80", "443"]
}
variable "common_tags" {
    type = map
    default = {
       Owner = "User owner name"
    }
}


provider "aws" {
access_key = "KEY"
secret_key = "SECRET"
region     = var.region
default_tags = var.common_tags
}


resource "aws_security_group" "my-sec-web" {
  name = "my-security-web-rule"
  vpc_id = aws_default_vpc.default.id
  dynamic "ingress" {
    for_each = var.open_ports
    content {
        from_port         = ingress.value
        to_port           = ingress.value
        protocol          = "tcp"
        cidr_blocks       = [var.cidr_block]       
    }
  }
  egress {
    from_port = 0
    to_port = 65535
    protocol = "-1"
    cidr_blocks = [var.cidr_block]
  }
  tags = var.common_tags, {
    Name = "Security Policy for web server"
  }
}
```
В наведеному прикладі існує змінна region, для якої не задано значення, тому тераформ завжди запитає користувача про її значення та змусить користувача його заповнити. Таким чином при застосуванні буде вводитися регіон де буде працювати тераформ.
Гарана практика всі змінні виносити в окремий файл variables.tf. description - виводиться при запиті значення змінної.
Крім того, змінна може мати значення за замовчуванням default, але тоді вона не буде примусово запистуватися при запуску, а для її зміни знадобиться спеціальний виклик.
Існують типи string, list, map, bool - вони не є обов'язвими для того, щоб їх вказувати, тераформ сам визначить там зі значення default, проте гарна практика в тому, що якщо ви тип вказали то терафрм перевірть, що вказаний тип співпадає з введеним, що дуже корисно для правильного заповнення значень.
Є можливість при застосуванні змінної типу map, об'єднання значнень зі змінної з додатковими ключами, як у прикладі з тегами.
Є також такого плану трюк:
`tags = merge(var.common_tags, {Name = "${var.common_tags["Enviriament"]} Security Policy for web server" })` і тут ім'я фомується прямо зі значенням яке береться з того є самого словника ключів.

## Автозаповнення змінних
Значення змінних можна змінити з командної строки, наприклад задати нове значення для регіону:
`terraform apply -var="region=us-east-1"` там можна змінити будь-які змінні. Ключ "-var", можна застосувати кілька разів, щоб змінити кілька змінних.
Також значення змінних можуть бути задані через змінні оточення:
```
export TF_VARS_region=us-east-2
terraform apply
```
Ще один варіант їх задати створити файл terraform.tfvars з необхідними значеннями в форматі "назва змінної" = "значення", по одному на строку:
```
region=us-east-2
```
Файл terraform.tfvars має більший преорітет ніж значення задані в default. Інша можливість створити файли *.auto.tfvars, наприклад
dev.auto.tfvars та prod.auto.tfvars. Якщо файлу terraform.tfvars не існує, а є лише один файлтипу *.auto.tfvars то буде застосовано його. Якщо файлів більше одного - буде помилка, що б вибрати файл потрібно застосувати команду `terraform apply -var=prod.auto.tfvars`. Ця ж каманда дозволяє застосувати для змінних будь який файл ".tfvars".
Детально тут https://developer.hashicorp.com/terraform/language/values/variables

## Локальні змінні
Припустимо потрібно створити комбінацію з інших змінних:
  `Name = "${var.var_1} - ${var.name_2}"`
Тоді якщо такий фрагмент буде використаний кілька разів, то його можна оптимізувати через створення локальної змінної:
```
locals {
   full_name = "${var.var_1} - ${var.name_2}"
}
....
    Name = local.full_name
....

```
Важливо відмітити, що локальні змінні створюються в блоці "locals", а застосовуються через ім'я "local".
Крім того в локальну змінну можна занести значення з data source.
```
locals {
   az_list = data.aws_availability_zones.available.names
   az_list_value = join(",",data.aws_availability_zones.available.names)
   location = "Zones: ${local.az_list_value} in region: ${data.region.current.description}"
}
```
Якщо значення az_list це список, то az_list_value це вже строка (бо вона з'єднана). Також можливо посилатися з одних локальних змынних на інші.

# Запуск локлаьних команд на хості тераформа
Під час створення ресурсів іноді виникає задача запустити локально процесс, наприклад щоб згенерувати ключі, для цього створюємо ресурс:
```
resource "null_resource" "command1" {
 provisioner "local-exec" {
  command = "echo "Test string" > local_file.txt
 }
}
resource "null_resource" "command2" {
  provisioner "local-exec" {
    command = "Get-Date > completed.txt"
    interpreter = ["PowerShell", "-Command"]
  }
}
resource "null_resource" "command3" {
  provisioner "local-exec" {
    command = "echo $FOO $BAR $BAZ >> env_vars.txt"

    environment = {
      FOO = "bar"
      BAR = 1
      BAZ = "true"
    }
  }
}

resource "aws_instance" "web" {
  # ...

  provisioner "local-exec" {
    command = "echo $FOO $BAR $BAZ >> env_vars.txt"

    environment = {
      FOO = "bar"
      BAR = 1
      BAZ = "true"
    }
  }
}
```
Основний момент, що ці команди виконуються проте не їх вивід не можу бути отриманий для подальшого використання. Якщо потрібно використати певний шел чи наприклад python, можна застосувати параметр interpreter де вказується інтрепретатор та його аргументи.
Також можливо задати для команди змінні оточення через параметр environment. Також частину визову команд можна розмістити в іншому ресурі, що створююється. Також на null_resource можна накласти залежності 
https://developer.hashicorp.com/terraform/language/resources/provisioners/local-exec

# Генерація паролей та їх зберігання
```
resource "random_string" "rds_passowrd" {
    length = 12
    special = true
    override_special = "@#!"
}

resource "aws_ssm_parameter" "rds_password" {
    name = "/prod/mysql"
    description = "Master password for MySQl"
    type = "SecureString"
    value = random_string.rds_passowrd.result
}
```
Цей фрагмент згенерує пароль через ресурс random_string в якому вказано довжина пароля та спеціальні символи які можуть бути в ньому.
Далі в Амазоні створюється захищений ресурс де зберігається пароль.
Загалом значення з aws_ssm можна дістати:
```
data "aws_ssm_parameter" "rds_password" {
    name = "/prod/mysql"
    depends-on = [aws_ssm_parameter.rds_password]
}
output "rds_password" {
  value = data.aws_ssm_parameter.rds_password.value
}
```
Наприклад це може бути застосовано для створення БД:
```
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  db_name              = "mydb"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  username             = "admin"
  password             = data.aws_ssm_parameter.rds_password.value
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true
}
```
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance
Проте при застосуванні такого скрипту буде завжди застосовуватися зміна пароля.

```
resource "random_string" "rds_passowrd" {
    length = 12
    special = true
    ovveride_special = "@#!"
    keepers = {
      keeper1 = var.var_1
      keeper2 = var.var_2
    }
}
```
Особливість цього блоку, що він завжди буде створюватися заново. І його значення не зберігається.
Можна вказати перелік змінних в keepers, тоді перестворення такого пароля буде лише якщо будь-яка зі змінних вказаних в keepers зміниться.
https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string#keepers-1

# Умови та цикли
## Умовні вирази

В тераформ можливо викорстання умовних виразів значення яких буде визначатися за умовами. Це тернарний оператор з мов програмування.
`X = УМОВА ? ЗНАЧЕННЯ_ЯКЩО_УМОВА_ДОСТОВІРНА : ЗНАЧЕННЯ_ЯКЩО_УМОВА_ХИБНА`
В умовах доступні наступні оператори "==" - точно дорівнює, "!=" - точно не дорівнює, ">", "<", "<=", ">=" - порівняння (більше\меньше), а також булеві оператори "&&" - "та", "||" - "або" та "!" - "ні".
Це можна використати наступним чином:
```
variable "env" {
    default = "prod"
}

resource "aws_instance" "api_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = (var.env == "prod" ? "t2.large" :"t2.micro")
}
```
Тоді різний тип ресурсу буде використано залежно від значення змінної env, що визначить в якому розгортається ресурс. А значення зміної можна задати або в файлі або при необхідності змінювати при запуску тераформ.
Інший фокус це умовне створення ресурсів:
```
variable "env" {
    default = "prod"
}

resource "aws_instance" "api_server_machine" {
  count = (var.env == "dev" ? 1 :0)
  ami = "ami-03250b0e01c28d196"
  instance_type = (var.env == "prod" ? "t2.large" :"t2.micro")
}
```
В цьому прикладі ресурс буде ствоерно лише коли значення env дорівнює "dev".
## Пошук значень
Поглянемо на такий код:
```
variable "ec2_size" {
    "prod" = "t2.large"
    "staging" = "t2.medium"
    "dev" = "t2.micro"
}

resource "aws_instance" "api_server_machine" {
  ami = "ami-03250b0e01c28d196"
  instance_type = lookup(var.ec2_size, "t2.micro")
}
```
Тут значення instance_type, вибирається зі словника ec2_size, який зберігає пари ключ - значеннями, здійснюється пошук ключа "t2.micro".
Функція lookup здійснює пошук значення в словнику та повертає значення, якщо значення немає:
X = lookup(СЛОВНИК, КЛЮЧ_ДЛЯ_ПОШУКУ)
Наприклад це можна застосувати так:
```
variable "env" {
    default = "prod"
}

variable "ec2_size" {
    "prod" = "t2.large"
    "staging" = "t2.medium"
    "dev" = "t2.micro"
}

resource "aws_instance" "api_server_machine" {
  count = (var.env == "dev" ? 1 :0)
  ami = "ami-03250b0e01c28d196"
  instance_type = lookup(var.ec2_size,var.env)
}

resource "aws_instance" "web_server_machine" {
  count = (var.env == "dev" ? 1 :0)
  ami = "ami-03250b0e01c28d196"
  instance_type = (var.env == "prod" ? var.ec2_size["prod"] :var.ec2_size["dev"])
}
```
Тут сервер створюється залежно від значення змінної "env", а також розмір сервера вибереться зі словника.
Також можна застосовувати отримання значення зі словника, як при створенні ресурсу "web_server_machine".

# Цикли та коунтери

## Count
Наприклад є задача створити перелів користувачів та створити кілька сервісів:
```
variable "ec2_users" {
    default = ["user1", "user2", "user3"]
}


resource "aws_iam_user" "users" {
  count = length(var.ec2_users)
  name = element(var.ec2_users, count.index)
}

resource "aws_instance" "web" {
  count = 5
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  tags = {
    Name = "Server ${count.index + 1}"
  }
}

output users_id {
   value = aws_iam_user.users[*].id
}
```
Для розв'язання цієї задачі використоується count, в першому випадку count задає кількість користувачів, що треба створити. Для того, щоб не визначати кількість вручну, використана функція length, що визначає довжину списку користувачів.
Далі для отримання імені користувача зі списку використана функція element, що дістає зі списку var.ec2_users користувачів по одному для кожного значення індексу "count.index".
В другій частині створюється 5 aws_instance, для кожного тега використано значення count.index, бо значення відраховуються від 0, його потрібно збільшити на 1 для зручності.
В кінці зроблено вивід всіх ідентифікаторів користувачів.
## for
Ось така штука може сгенерувати список значень на основі створених користувачів:
```
output output_created_users {
   value = [
      for user in aws_iam_user.users:
      "User name= ${user.name} has ARN=${user.arn}
   ]
}

output output_created_users_map {
   value = {
      for user in aws_iam_user.users:
      user.name => user.arn
   }
}
```
Другий вивід сгенерує словник з імен та їх АРН.
Варіант це отримання значень тільки за умовою:
```
output output_created_users {
   value = [
       for user in aws_iam_user.users:
       user.name
       if length(user.name) > 4 
]
}
```
В результуючий список потраплять тільки імена користувачів з довжиною імені більше 4.

# Використання кількох провайдерів
В нашому файлі конфігурації можна використати кілька провайдерів одночасно. Проте в такому випадку всі, крім того, що буде використаний за замовчуванням повинні мати параметр alias.
В такому випадку всі ресурси для яких не задано параметр provider, використовують той що не маж alias,  а коли він заданий то використовується той, що вказаний.
```
provider "aws" {
   region     = "ca-central-1"
}

provider "aws" {
   region     = "us-east-1"
   alias = "usa"
}


resource "aws_instance" "web_server_machine1" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t2.micro"
}

resource "aws_instance" "web_server_machine1" {
  ami = "ami-03250b0e01c28d196"
  instance_type = "t2.micro"
  provider = aws.usa
}
```
В прикладі web_server_machine1 буде стоврено в регіоні "ca-central-1", а web_server_machine1, буде створено в регіоні us-east-1, це буде зроблено одночасно.
Параметр provider, може застосовуватися не тільки для ресурсів, а й для дата блоків.

# Remote State
Наприклад, маємо наступну конфігурацію:
```
provider "aws" {
   region     = "ca-central-1"
}

variable "vpc_cidr" {
    default = "10.0.0.0/16"
}

resource "aws_vpc" "my_vpc" {  
  cidr_block = var.vpc_cidr
  tags = {
     Name = "My VPC"
  }
}
```
Проте при звичайній роботі, файл зі стейтом створюється локально, але є можливість винести зберігання в хмару та дозволити спільну роботу з ними. Крім того можна переносити значення між проектами тераформ.
Наприклад в АМАЗОН під це можна використати Amazon "S3 Buckets", для цього йжемо в "Amazon S3 консоль" далі в "Buckets" а далі створюємо "Create bucket".
При створенні важливо вказати правильний регіон, використати шифрування "encryption" и дуже важливо ввімкнути підтримку версійності. Що важливо для роботи з велики інфраструктурами, якщо хтось внесе зміни можна буде їх відкатити.
Назва яку ми хзадаємо дуже важлива і головне повинна бути унікальною.
Для того, щоб тераформ використав зовнішнє сховище прописуємо, після блоку провайдер:
```
provider "aws" {
   region     = "ca-central-1"
}

terraform {
  backend "S3" {
      backet = "<назва бакета, що була задана при його створенні>"
      key = "<ключ, що виступає як шлях до файлу>"
      region     = "ca-central-1"
  }
}
```
Один backet бажано використовувати єдиний для всього проекту, а от key, для кожної конфігурації окремий. key задається в формі шляху, наприклад "dev/network/terraform.tfstate"
Після таких налаштувань tfstate буде зберігатися в хмарі, проте файли провайдерів будуть зберігатися локально.
```
terraform {
   backend "S3" {
      backet = "project1_terraform_backet"
      key = "dev\project1\terraform.tfstate"
      region     = "ca-central-1"
   }
}
```
ВАЖЛИВО: всі змінні, що прописані як output, можна буде отримати з інших проектів.
Наприклад, змінимо початковий файл:
```
provider "aws" {
   region     = "ca-central-1"
}

terraform {
   backend "S3" {
      backet = "project1_terraform_backet"
      key = "dev\project1\terraform.tfstate"
      region     = "ca-central-1"
   }
}

variable "vpc_cidr" {
    default = "10.0.0.0/16"
}

resource "aws_vpc" "my_vpc" {  
  cidr_block = var.vpc_cidr
  tags = {
     Name = "My VPC"
  }
}

output my_vpc_id {
   value = aws_vpc.my_vpc.id
}

output vpc_cyder_block {
   value = aws_vpc.my_vpc.cidr_block
}

```




Концепція публічних і приватних сабнетів (subnets) в AWS базується на тому, чи можуть ресурси в сабнеті напряму спілкуватися з інтернетом чи ні.

🧠 Основна ідея
```
|Тип сабнета|	Має доступ в Інтернет?	       |Публічна IP?    |	Використання               |
|Публічний  |	✅ через Internet Gateway (IGW)|	✅ напряму	|Web-сервери, ALB/NLB          |
|Приватний  |	❌ напряму                     |	❌	        |ECS, бази даних, внутрішні API|
```
📦 Приклад архітектури:
```
AWS VPC (10.0.0.0/16)
├── Public Subnets (10.0.0.0/24, 10.0.1.0/24)
│   ├── ALB / NLB
│   └── Bastion host (SSH)
│
├── Private Subnets (10.0.2.0/24, 10.0.3.0/24)
├── ECS Fargate Tasks
└── RDS / ElastiCache
```
✅ Публічні сабнети — призначення:
 - Розміщення ресурсів, які напряму доступні з Інтернету
 - Наявність Internet Gateway
 - EC2 з публічними IP або Load Balancer'и

Bastion host (для SSH до приватних EC2)

📌 Типовий приклад:
 - Application Load Balancer або Network Load Balancer
 - Jump host (bastion) для доступу до приватної частини інфраструктури

🔒 Приватні сабнети — призначення:
 - Ресурси, які не повинні мати прямий доступ ззовні
 - Не мають IGW, іноді — мають NAT Gateway (якщо потрібно виходити в інтернет для оновлень)
 - ECS Tasks, RDS, EFS, внутрішні мікросервіси

📌 Типовий приклад:
 - ECS (Fargate або EC2) tasks
 - Amazon RDS (PostgreSQL, MySQL)
 - Internal API, backend-логіка

🔄 Взаємодія:
```
|Ресурс     |	Сабнет	 |Доступ до Інтернету       |	Доступ до ALB/NLB |
|ECS Task   |	Приватний|	❌ (або ✅ через NAT)	|✅ через ALB/NLB     |
|ALB/NLB    |	Публічний|	✅                      |	❌                |
|EC2 Bastion|	Публічний|	✅                      |	✅                |
|RDS        |	Приватний|	❌                      |	✅ (з приватних)  |
```
📏 Рекомендації щодо кількості сабнетів:
Мінімум по 2 публічних і 2 приватних сабнети (по одній на кожну Availability Zone — для HA)

Якщо використовуєш ECS, RDS, ALB — поділи на 2-3 AZ:
 - subnet-public-eu-central-1a
 - subnet-public-eu-central-1b
 - subnet-private-eu-central-1a
 - subnet-private-eu-central-1b

✅ Best practices:
Розміщуй інтернет-фейс ресурси (ALB, bastion) в публічних сабнетах
 - ECS / RDS / внутрішні сервіси — в приватних
 - Захищай приватні сабнети через security groups і routing
 - Відокремлюй staging/prod середовища на рівні сабнетів або VPC
 - Ніколи не розміщуй бази даних у публічному сабнеті

Приклад, приватні мережі з виходом в інтернет через НАТ
```
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-igw"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  tags = {
    Name = "main-nat"
  }
  depends_on = [aws_internet_gateway.igw]
}

resource "aws_eip" "nat" {
  vpc = true
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "public-subnet-${count.index}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index + 2)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "private-subnet-${count.index}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

data "aws_availability_zones" "available" {}
```
Приклад aws_vpc з приватними мережами без виходу в інтернет
```
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-igw"
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "public-subnet-${count.index}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index + 2)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "private-subnet-${count.index}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

data "aws_availability_zones" "available" {}
```
Приклад балансера для HTTP сервіса
```
resource "aws_lb" "app" {
  name               = "app-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = var.port_list[0]
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200-399"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```
Приклад балансера на рівні сокетів
```
resource "aws_lb" "app" {
  name               = "app-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = var.port_list[0]
  protocol = "TCP"
  target_type = "ip"
  vpc_id   = aws_vpc.main.id

  health_check {
    protocol            = "TCP"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "tcp" {
  load_balancer_arn = aws_lb.app.arn
  port              = var.port_list[0]
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```