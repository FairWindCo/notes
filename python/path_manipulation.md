# отримати перелык файлів за шаблоном 
Path.rglob(pattern, *, case_sensitive=None)
case_sensitive інсує починаючи з 3.12
Наприклад:
`sorted(Path().rglob("*.py"))`

Видасть такий результат:
```
[PosixPath('build/lib/pathlib.py'),
 PosixPath('docs/conf.py'),
 PosixPath('pathlib.py'),
 PosixPath('setup.py'),
 PosixPath('test_pathlib.py')]
```

[https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob]
