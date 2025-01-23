import sqlite3
import json
import codecs
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
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET stars = stars + ? WHERE email = ?", (stars_n, email))
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



# a = {
#     "email": "ivan@ivanov.ru",
#     "stars": 5,
#     "test_num": 1
# }

# with open('star.json', 'w', encoding='utf-8') as json_file:
#     json.dump(a, json_file, ensure_ascii=False, indent=4)
add_user('auth.json')
