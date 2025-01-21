import sqlite3

db_lp = sqlite3.connect('ItPying_users.db')
cursor_db = db_lp.cursor()

sql_create = '''CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    class TEXT,
    raiting INT,
    stars INT,
    teacher TEXT);'''

sql_create2 = '''CREATE TABLE tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    right_answer TEXT NOT NULL,
    status TEXT NOT NULL
);'''

cursor_db.execute(sql_create)
cursor_db.execute(sql_create2)

db_lp.commit()
db_lp.close()