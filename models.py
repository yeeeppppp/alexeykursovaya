"""
Модели данных для настольного приложения продажи автомобилей.
В десктоп-версии мы используем SQLite напрямую, поэтому 
этот файл здесь используется только как документация структуры.
Фактическая схема базы данных создается в database.py
"""

# Структура таблицы cars
# id INTEGER PRIMARY KEY AUTOINCREMENT
# name TEXT NOT NULL
# price REAL NOT NULL
# specifications TEXT NOT NULL 
# image BLOB

# Структура таблицы admins
# id INTEGER PRIMARY KEY AUTOINCREMENT
# username TEXT UNIQUE NOT NULL
# password TEXT NOT NULL