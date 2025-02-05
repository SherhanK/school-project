import sqlite3
import json
import subprocess
from datetime import date


def auth(file):
    try:
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
                    with open('answer.json', 'w', encoding='utf-8') as json_file:
                        json.dump(user_info, json_file, ensure_ascii=False, indent=4)

            elif role == 'Учитель':
                conn = sqlite3.connect('ItPying_users.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
                teacher_name = cursor.fetchone()[0]
                cursor.execute("SELECT name, stars, class FROM users WHERE teacher = ? AND role = 'Ученик'", (teacher_name,))
                students = cursor.fetchall()
                conn.close()
                student_list = [{"name": student[0], "stars": student[1], "class": student[2]} for student in students]
                user_info = {
                    "name": teacher_name,
                    "role": role,
                    "students": student_list
                }
                with open('answer.json', 'w', encoding='utf-8') as json_file:
                    json.dump(user_info, json_file, ensure_ascii=False, indent=4)
        else:
            with open('answer.json', 'w', encoding='utf-8') as f:
                json.dump({"message": "Неправильный логин или пароль"}, f, ensure_ascii=False, indent=4)

    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except ValueError as e:
        error_data = {
            "error": "UserNotFoundError",
            "message": str(e),
            "details": f"Пользователь с email {email} не найден."
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except sqlite3.Error as e:
        error_data = {
            "error": "DatabaseError",
            "message": "Произошла ошибка в базе данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при аутентификации.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)



def star_add(file):
    try:
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
        cursor.execute("INSERT INTO test_status (student_id, id_task, result, date) VALUES (?, ?, ?, ?)", (user_id, task_num, '1/1', today.strftime("%d.%m.%Y")))
        cursor.execute("SELECT id_test FROM test_status WHERE student_id = ? ORDER BY id_test DESC LIMIT 1", (user_id,))
        test_num = cursor.fetchone()[0]
        cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))

        if not cursor.fetchone():
            cursor.execute("INSERT INTO student_tasks (id_student, id_test, id_task, best_result) VALUES (?, ?, ?, ?)", (user_id, test_num, task_num, "1/1"))
        else:
            cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))
            last_test = cursor.fetchone()[0]
            now_test = f"{last_test}/{test_num}"
            cursor.execute("UPDATE student_tasks SET id_test =  ? WHERE id_student = ? AND id_task = ?", (now_test, user_id, task_num))
        conn.commit()
        conn.close()

        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump({"message": "Задание успешно добавлено."}, f, ensure_ascii=False, indent=4)

    except ValueError as e:
        error_data = {
            "error": "UserNotFoundError",
            "message": str(e),
            "details": f"Пользователь с email {email} не найден."
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при добавлении выполненного задания.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


def add_user(file):
    try:
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

        with open('answer.json', 'w', encoding='utf-8') as f:
            json.dump({"message": "Пользователь успешно добавлен."}, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при добавлении пользователя.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

def check_stars_class(file):
    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        clas = data['class']
        teacher = data['teacher']

        conn = sqlite3.connect('ItPying_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, stars FROM users WHERE class = ? AND teacher = ?", (clas, teacher))
        result = cursor.fetchall()
        conn.close()

        if result:
            user_info = {
                "students": [{"name": name, "stars": stars} for name, stars in result]
            }
            with open('answer.json', 'w', encoding='utf-8') as json_file:
                json.dump(user_info, json_file, ensure_ascii=False, indent=4)

    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


    except sqlite3.OperationalError as e:
        error_data = {
            "error": "OperationalError",
            "message": "Произошла ошибка при выполнении запроса к базе данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except sqlite3.IntegrityError as e:
        error_data = {
            "error": "IntegrityError",
            "message": "Произошла ошибка при выполнении запроса к базе данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при проверке звезд класса.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


def binary_to_python(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        binary_code = data.get("code", "")
        byte_chunks = [binary_code[i:i + 8] for i in range(0, len(binary_code), 8)]
        ascii_string = ''.join([chr(int(b, 2)) for b in byte_chunks])

        with open("py_task.py", 'w', encoding='utf-8') as py_file:
            py_file.write(ascii_string)

    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "UnknownError",
            "message": "Ошибка при преобразовании бинарного кода в Python-скрипт.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


def run_task():
    try:
        with open("tasks.json", 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        with open("test.json", 'r', encoding='utf-8') as f:
            comp_data = json.load(f)
        task_num = comp_data['task_num']
        task = next((task for task in tasks_data['tasks'] if task['num'] == task_num), None)
        email = comp_data['email']
        star_n = comp_data['stars']
        io_tests = task['io_data']
        passed_tests = 0
        failed_tests = 0
        passed_test_numbers = []

        for i, test in enumerate(io_tests):
            input_data = test['input']
            expected_output = test['output'].strip()
            result = subprocess.run(
                ['python', 'py_task.py'],
                input=input_data,
                text=True,
                capture_output=True
            )
            actual_output = result.stdout.strip()
            if actual_output == expected_output:
                passed_tests += 1
                passed_test_numbers.append(i + 1)
            else:
                failed_tests += 1

        res = f"{passed_tests}/{passed_tests + failed_tests}"
        conn = sqlite3.connect('ItPying_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
        today = date.today()
        cursor.execute("INSERT INTO test_status (student_id, id_task, result, date, bin_code) VALUES (?, ?, ?, ?, ?)", (user_id, task_num, res, today.strftime("%d.%m.%Y"), comp_data['code']))
        cursor.execute("SELECT id_test FROM test_status WHERE student_id = ? ORDER BY id_test DESC LIMIT 1", (user_id,))
        test_num = cursor.fetchone()[0]
        cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))

        if not cursor.fetchone():
            cursor.execute("INSERT INTO student_tasks (id_student, id_test, id_task, best_result) VALUES (?, ?, ?, ?)", (user_id, test_num, task_num, res))
        else:
            cursor.execute("SELECT id_test FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))
            last_test = cursor.fetchone()
            last_test_num = ""
            for i in range(len(last_test)):
                last_test_num += last_test[i]
            now_test = f"{last_test_num}/{test_num}"
            cursor.execute("SELECT best_result FROM student_tasks WHERE id_student = ? AND id_task = ?", (user_id, task_num))
            max_result = cursor.fetchone()[0]
            al = max_result.split('/')[0]
            an = res.split('/')[0]
            if int(an) > int(al):
                cursor.execute("UPDATE student_tasks SET id_test =  ?, best_result = ? WHERE id_student = ? AND id_task = ?", (now_test, res, user_id, task_num))
            else:
                cursor.execute("UPDATE student_tasks SET id_test =  ? WHERE id_student = ? AND id_task = ?", (now_test, user_id, task_num))

        if passed_tests == passed_tests + failed_tests:
            cursor.execute("UPDATE users SET stars = stars + ? WHERE email = ?", (star_n, email))
        conn.commit()
        conn.close()

        result_data = {
            "correct": passed_tests,
            "total": passed_tests + failed_tests,
            "passed_tests_numbers": passed_test_numbers
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)

    except ValueError as e:
        error_data = {
            "error": "UserNotFoundError",
            "message": str(e),
            "details": f"Пользователь с email {email} не найден."
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при компиляции кода.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


def check_tests_for_user(file):
    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        email = data['email']

        conn = sqlite3.connect('ItPying_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT id_test, id_task, best_result FROM student_tasks WHERE id_student = ?", (user_id,))
        tests = cursor.fetchall()
        conn.close()
        test_data = []
        for test in tests:
            result_data = {
                "id_test": test[0].split('/'),
                "id_task": test[1],
                "best_result": test[2]
            }
            test_data.append(result_data)
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except sqlite3.Error as e:
        error_data = {
            "error": "DatabaseError",
            "message": "Ошибка при работе с базой данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except ValueError as e:
        error_data = {
            "error": "UserNotFoundError",
            "message": str(e),
            "details": f"Пользователь с email {email} не найден."
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)


def check_test(file):
    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        id_test = data['id_test']
        id_task = data['id_task']
        email = data['email']

        conn = sqlite3.connect('ItPying_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT result, date, bin_code FROM test_status WHERE id_task = ? AND id_test = ? AND student_id = ?", (id_task, id_test, user_id))
        result = cursor.fetchone()
        conn.close()
        result_data = {
            "result": result[0],
            "date": result[1],
            "bin_code": result[2]
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)

    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except sqlite3.Error as e:
        error_data = {
            "error": "DatabaseError",
            "message": "Ошибка при работе с базой данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

def check_file_type(file):
    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        func_type = data['type']

        if func_type == "auth":
            auth(file)
        elif func_type == "done_task":
            star_add(file)
        elif func_type == "add_student":
            add_user(file)
        elif func_type == "class_stars":
            check_stars_class(file)
        elif func_type == "code_task":
            binary_to_python(file)
            run_task()

    except FileNotFoundError as e:
        error_data = {
            "error": "FileNotFoundError",
            "message": f"Файл {file} не найден.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        error_data = {
            "error": "JSONDecodeError",
            "message": "Некорректный формат JSON в файле.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except TypeError as e:
        error_data = {
            "error": "TypeError",
            "message": "Некорректный тип данных.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
    
    except AttributeError as e:
        error_data = {
            "error": "AttributeError",
            "message": "Некорректный атрибут.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        error_data = {
            "error": "CriticalError",
            "message": "Произошла критическая ошибка при обработке файла.",
            "details": str(e)
        }
        with open("answer.json", 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)
