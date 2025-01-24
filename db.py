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

sql_create2 = '''CREATE TABLE tasks_status(
    id_test INTEGER,
    student_id INTEGER PRIMARY KEY REFERENCES users(id),
    id_task INTEGER,
    result TEXT,
    bin_code TEXT,
    date DATE
);'''

sql_create3 = '''CREATE TABLE student_tasks(
    id_student INTEGER PRIMARY KEY REFERENCES users(id),
    id_test INTEGER,
    id_task INTEGER
);'''

cursor_db.execute(sql_create)
cursor_db.execute(sql_create2)
cursor_db.execute(sql_create3)

db_lp.commit()
db_lp.close()
