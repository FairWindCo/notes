# Оновлення пакетів
## подивитися перелік пакетів які застаріли
```
pip list --outdated
```

## Оновлення всіх застарылих пакетів під Windows
```pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}```

## Оновлення всіх застарылих пакетів під Ubuntu
```pip3 list -o | cut -f1 -d' ' | tr " " "\n" | awk '{if(NR>=3)print}' | cut -d' ' -f1 | xargs -n1 pip3 install -U ```

## Більш кероване оновлення через requirements
### Формування списку встановлених пакетів
```pip freeze > requirements.txt```

Редагуємо список пакетів, зміюємо символ "==", на ">="

Виконуємо команду:
```pip install -r requirements.txt --upgrade```

## Оновлення всередині Virtual Environment
в середині середовища виконати скрипт:
```
import pkg_resources
from subprocess import callfor dist in pkg_resources.working_set:
    call("python -m pip install --upgrade " + dist.<projectname>, shell=True)
```

## Оновлення всередині Pipenv Environment
Заходимо в шел
```pipenv shell```
Виконуэмо оновлення:
```
pipenv update
```


[source](https://www.activestate.com/resources/quick-reads/how-to-update-all-python-packages/)
