import subprocess
import json
import bson
def convert_bin_to_py(bin_file):
    with open(bin_file, 'rb') as bfile:
        data = bson.deserialize(bfile.read())
    with open("py_tasks.py", 'w', encoding='utf-8') as pfile:
        pfile.write("data = ")
        pfile.write(json.dumps(data, indent=4))

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

if __name__ == "__main__":
    run_task()