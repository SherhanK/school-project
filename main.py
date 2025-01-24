import sqlite3
import json
import codecs
import bson
import subprocess
from datetime import date
def auth(file):
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    email = data['email']
    
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
    role_result = cursor.fetchone()
    role = role_result[0]
    conn.close()

    if result and data['password'] == result[0]:
        if role == 'Ученик':
            conn = sqlite3.connect('ItPying_users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT role, name, class, raiting, stars, teacher FROM users WHERE email = ?", (email,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                role, name, class_, raiting, stars, teacher = user_data
                user_info = {
                    "name": name,
                    "role": role,
                    "class": class_,
                    "rating": raiting,
                    "stars": stars,
                    "teacher": teacher
                }
                with open('user_info.json', 'w', encoding='utf-8') as json_file:
                    json.dump(user_info, json_file, ensure_ascii=False, indent=4)
                return user_info
        if role == 'Учитель':
            conn = sqlite3.connect('ItPying_users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT role, name FROM users WHERE email = ?", (email,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                role, name = user_data
                user_info = {
                    "name": name,
                    "role": role
                }
                with open('user_info.json', 'w', encoding='utf-8') as json_file:
                    json.dump(user_info, json_file, ensure_ascii=False, indent=4)
                return user_info


def star_add(file):
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    email = data['email']
    stars_n = data['stars']
    task_num = data['task_num']
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET stars = stars + ? WHERE email = ?", (stars_n, email))
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user_id = cursor.fetchone()[0]
    today = date.today()
    cursor.execute("INSERT INTO tasks_status (student_id, id_task, result, date) VALUES (?, ?, ?, ?)", (user_id, task_num, '100/100', today.strftime("%d.%m.%Y")))
    cursor.execute("SELECT id_test FROM tasks_status WHERE student_id = ? ORDER BY id_test DESC LIMIT 1", (user_id,))
    test_num = cursor.fetchone()[0]
    cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO student_tasks (id_student, id_test, id_task) VALUES (?, ?, ?)", (user_id, test_num, task_num))
    else:
        cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))
        last_test = cursor.fetchone()[0]
        now_test = f"{last_test}/{test_num}"
        cursor.execute("UPDATE student_tasks SET id_test =  ? WHERE id_student = ? AND id_task = ?", (now_test, user_id, task_num))
    conn.commit()
    conn.close()
    return True

def add_user(file):
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    name = data['name']
    email = data['email']
    password = data['password']
    role = data['role']
    clas = data['class']
    teacher = data['teacher']
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password, role, class, stars, raiting, teacher) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, email, password, role, clas, 0, 0, teacher))
    conn.commit()
    conn.close()
    return True

def check_stars_class(file):
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    clas = data['class']
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT stars, name FROM users WHERE class = ?", (clas))
    result = cursor.fetchall()
    conn.close()
    if result:
        stars, name = result
        user_info = {
            "name": name,
            "stars": stars
        }
        with open('user_info.json', 'w', encoding='utf-8') as json_file:
            json.dump(user_info, json_file, ensure_ascii=False, indent=4)
        return user_info
