#!/bin/bash

# Функция для проверки прав суперпользователя
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Пожалуйста, запустите этот скрипт с правами суперпользователя (sudo)"
        exit 1
    fi
}

# Функция для установки зависимостей для Python
install_python_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo "Python3 не установлен! Устанавливаем..."
        if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
            sudo apt update
            sudo apt install -y python3 python3-venv
        elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
            echo "Для Windows установите Python вручную!"
            exit 1
        fi
    fi
}

# Функция для установки зависимостей для Node.js
install_node_dependencies() {
    if ! command -v npm &> /dev/null; then
        echo "npm не установлен! Устанавливаем Node.js и npm..."
        if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
            sudo apt update
            sudo apt install -y nodejs npm
        elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
            echo "Для Windows установите Node.js и npm вручную!"
            exit 1
        fi
    fi
}

# Функция для создания и активации виртуальной среды
create_virtualenv() {
    VENV_DIR="venv"
    echo "Создаем виртуальную среду..."
    python3 -m venv $VENV_DIR

    echo "Активируем виртуальную среду..."
    if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
        source $VENV_DIR/bin/activate
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
        .\\$VENV_DIR\\Scripts\\activate
    fi
}

# Функция для установки зависимостей Python
install_python_requirements() {
    echo "Устанавливаем зависимости для Python..."
    pip install --upgrade pip
    pip install -r requirements.txt || { echo "Ошибка установки зависимостей Python!"; exit 1; }
}

# Функция для установки зависимостей фронтенда
install_frontend_dependencies() {
    echo "Устанавливаем зависимости для фронтенда..."
    cd API/front || { echo "Папка 'API/front' не найдена!"; exit 1; }
    npm install || { echo "Ошибка установки зависимостей фронтенда!"; exit 1; }
    cd ../..
}

# Функция для запуска бэкенда
run_backend() {
    echo "Запускаем бэкенд..."
    python3 API/main_server.py &
}

# Функция для запуска фронтенда
run_frontend() {
    echo "Запускаем фронтенд..."
    cd API/front || { echo "Папка 'API/front' не найдена!"; exit 1; }
    npm start -- --port 3000
    cd ../..
}

# Основной процесс

# Проверка прав суперпользователя для Linux/macOS
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    check_root
fi

# Установка зависимостей для Python
install_python_dependencies

# Установка зависимостей для Node.js
install_node_dependencies

# Создание и активация виртуальной среды
create_virtualenv

# Установка зависимостей для Python
install_python_requirements

# Установка зависимостей для фронтенда
install_frontend_dependencies

# Запуск бэкенда
run_backend

# Запуск фронтенда
run_frontend
