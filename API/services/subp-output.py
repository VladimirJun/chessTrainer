import subprocess
import configparser as conf
import os
import re

# Чтение конфигурационного файла
config = conf.RawConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '../system_files/config.properties')
config.read(config_path)

# Путь к движку
engine_path = config.get("Main", "EngineStr")

# Запуск движка
process = subprocess.Popen(
    engine_path,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    bufsize=1
)

def send_command(cmd):
    """Отправляет команду движку"""
    process.stdin.write(cmd + "\n")
    process.stdin.flush()

def read_response():
    """Читает ответ движка"""
    output = []
    while True:
        line = process.stdout.readline().strip()
        if line == "":
            break  # Прерываем чтение при пустой строке
        output.append(line)
    return output

# 1️⃣ Инициализируем движок
send_command("uci")
send_command("isready")
print("\n".join(read_response()))

# 2️⃣ Устанавливаем позицию
send_command("position startpos")

# 3️⃣ Запрашиваем eval (детализированный анализ)
send_command("eval")
eval_output = read_response()

# Инициализация переменных для оценки
Material_MG_W, Material_EG_W, Material_MG_B, Material_EG_B = 0.0, 0.0, 0.0, 0.0
Mobility_MG_W, Mobility_EG_W, Mobility_MG_B, Mobility_EG_B = 0.0, 0.0, 0.0, 0.0
KingSafety_MG_W, KingSafety_EG_W, KingSafety_MG_B, KingSafety_EG_B = 0.0, 0.0, 0.0, 0.0
Threats_MG_W, Threats_EG_W, Threats_MG_B, Threats_EG_B = 0.0, 0.0, 0.0, 0.0
Space_MG_W, Space_EG_W, Space_MG_B, Space_EG_B = 0.0, 0.0, 0.0, 0.0
Initiative_W, Initiative_B = 0.0, 0.0
def total_evaluation():
    global Total_evaluation
    Total_evaluation = Total_evaluation = (
    Material_MG_W + Material_EG_W - Material_MG_B - Material_EG_B +
    Mobility_MG_W + Mobility_EG_W - Mobility_MG_B - Mobility_EG_B +
    KingSafety_MG_W + KingSafety_EG_W - KingSafety_MG_B - KingSafety_EG_B +
    Threats_MG_W + Threats_EG_W - Threats_MG_B - Threats_EG_B +
    Space_MG_W + Space_EG_W - Space_MG_B - Space_EG_B +
    Initiative_W - Initiative_B
)
    return Total_evaluation
# Вычисляем total_evaluation вручную
Total_evaluation = 0.0

pattern = re.compile(r"(\w[\w\s]+)\s*\|\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*\|\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)")

for line in eval_output:
    match = pattern.match(line)
    if match:
        term, mg_white, eg_white, mg_black, eg_black = match.groups()
        term = term.strip().lower().replace(" ", "_")

        if term == "material":
            Material_MG_W, Material_EG_W, Material_MG_B, Material_EG_B = map(float, [mg_white, eg_white, mg_black, eg_black])
        elif term == "mobility":
            Mobility_MG_W, Mobility_EG_W, Mobility_MG_B, Mobility_EG_B = map(float, [mg_white, eg_white, mg_black, eg_black])
        elif term == "king_safety":
            KingSafety_MG_W, KingSafety_EG_W, KingSafety_MG_B, KingSafety_EG_B = map(float, [mg_white, eg_white, mg_black, eg_black])
        elif term == "threats":
            Threats_MG_W, Threats_EG_W, Threats_MG_B, Threats_EG_B = map(float, [mg_white, eg_white, mg_black, eg_black])
        elif term == "space":
            Space_MG_W, Space_EG_W, Space_MG_B, Space_EG_B = map(float, [mg_white, eg_white, mg_black, eg_black])
        elif term == "initiative":
            Initiative_W, Initiative_B = float(mg_white), float(mg_black)

# **Считаем Total Evaluation как сумму всех факторов**
total_evaluation()

# 7️⃣ Выводим результаты
print("\nРезультаты подробного анализа:")
print(f"Material MG (White): {Material_MG_W}, Material MG (Black): {Material_MG_B}")
print(f"King Safety MG (White): {KingSafety_MG_W}, King Safety MG (Black): {KingSafety_MG_B}")
print(f"Threats MG (White): {Threats_MG_W}, Threats MG (Black): {Threats_MG_B}")
print(f"Mobility MG (White): {Mobility_MG_W}, Mobility MG (Black): {Mobility_MG_B}")
print(f"Space MG (White): {Space_MG_W}, Space MG (Black): {Space_MG_B}")
print(f"Initiative (White): {Initiative_W}, Initiative (Black): {Initiative_B}")
print(f"Total Evaluation: {Total_evaluation}")

# 8️⃣ Завершаем работу движка
send_command("quit")
process.terminate()