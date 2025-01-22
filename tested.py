import subprocess
import json

def process_json_file(json_file):
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

    with open("comp.json", 'r', encoding='utf-8') as f:
        comp_data = json.load(f)

    task_num = comp_data['task_num']
    task = tasks_data['tasks'][task_num]

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

    print(f"\nВсего тестов: {passed_tests + failed_tests}")
    print(f"Пройдено тестов: {passed_tests}")
    print(f"Не пройдено тестов: {failed_tests}")




process_json_file("test.json")
run_task()
