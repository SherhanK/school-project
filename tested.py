import subprocess
import json
import sqlite3
from datetime import date

def binary_to_python(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    binary_code = data.get("code", "")

    byte_chunks = [binary_code[i:i + 8] for i in range(0, len(binary_code), 8)]
    ascii_string = ''.join([chr(int(b, 2)) for b in byte_chunks])
    
    with open("py_task.py", 'w', encoding='utf-8') as py_file:
        py_file.write(ascii_string)

def run_task():
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
            print(f"Тест {i + 1}: Пройден.")
            passed_tests += 1
        else:
            print(f"Тест {i + 1}: Не пройден.")
            print("  Ожидалось:", expected_output)
            print("  Получено:", actual_output)
            failed_tests += 1
    res = f"{passed_tests}/{passed_tests + failed_tests}"
    conn = sqlite3.connect('ItPying_users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user_id = cursor.fetchone()[0]
    today = date.today()
    cursor.execute("INSERT INTO tasks_status (student_id, id_task, result, date, bin_code) VALUES (?, ?, ?, ?, ?)", (user_id, task_num, res, today.strftime("%d.%m.%Y"), comp_data['code']))
    cursor.execute("SELECT id_test FROM tasks_status WHERE student_id = ? ORDER BY id_test DESC LIMIT 1", (user_id,))
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
    print(f"\nВсего тестов: {passed_tests + failed_tests}")
    print(f"Пройдено тестов: {passed_tests}")
    print(f"Не пройдено тестов: {failed_tests}")
