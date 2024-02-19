# in memory DB for python
## Stones
  [https://github.com/croqaz/Stones]
The idea behind this project is to have a common interface for a multitude of persistent key-value stores, easy to use and extend, with some extra built-in features as bonus. Inspired from Datastore and MemDown.

## tinydb
[https://github.com/msiemens/tinydb]
TinyDB is a lightweight document oriented database optimized for your happiness :) It's written in pure Python and has no external dependencies. The target are small apps that would be blown away by a SQL-DB or an external database server.
## viperdb
 [https://pypi.org/project/viperdb/]
  ViperDB is a lightweight embedded key-value store written in pure Python. It has been designed for being extremely simple while efficient.

Features
- tiny: the main db file consists of just ~300 lines of code.
- highly coverage: thanks to the small codebase, every single line of code is tested.
- log-structured: ViperDB takes design concepts by log-structured databases such as Bitcask.
- written in pure Python: no external dependency needed.
  проте зупинено в 22 році

  ## dbm
  [https://remusao.github.io/posts/python-dbm-module.html]
  Python is, in a lot of ways, a very rich language. After years of using it, I still regularly discover new parts of the ecosystem, even in the standard library. In particular, there are a few modules which are not very well-known, but can be very useful in some situations. Today I discovered dbm a persistent key/value store:

Quick start:
```
import dbm

with dbm.open('my_store', 'c') as db:
  db['key'] = 'value'
  print(db.keys()) # ['key']
  print(db['key']) # 'value'
  print('key' in db) # True
```
It behaves a lot like a dict except:
- It persists its values on disk
- You can only use str or bytes as key and values

## yedb
[https://pypi.org/project/yedb/]
YEDB is absolutely reliable rugged key-value database, which can survive in any power loss, unless the OS file system die. Keys data is saved in the very reliable way and immediately flushed to disk (this can be disabled to speed up the engine but is not recommended - why then YEDB is used for).
