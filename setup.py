from setuptools import setup, find_packages

# Чтение зависимостей из requirements.txt
with open("API/requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="my_project",
    version="1.0.0",
    packages=find_packages(),
    install_requires=required_packages,
    entry_points={
        'console_scripts': [
            'ChessAI=API.main_server:main',  # для запуска через команду `ChessAI`
        ],
    },
)
