#!/usr/bin/env python3
"""
Скрипт для запуска тестов.
"""
import subprocess
import sys
import os

def run_tests():
    """Запуск тестов с различными конфигурациями."""

    # Проверяем наличие pytest
    try:
        import pytest
    except ImportError:
        print("pytest не установлен. Установите его с помощью: pip install pytest")
        return False

    # Определяем команды для запуска тестов
    test_commands = [
        # Запуск всех тестов
        ["pytest", "-v", "--tb=short"],

        # Запуск тестов с покрытием
        ["pytest", "--cov=src", "--cov-report=html", "--cov-report=term"],
    ]

    print("Выберите тип тестов для запуска:")
    print("1. Все тесты")
    print("2. Все тесты с покрытием")
    print("3. Выход")

    try:
        choice = input("Введите номер: ").strip()

        if choice == "1":
            cmd = test_commands[0]
        elif choice == "2":
            cmd = test_commands[1]
        elif choice == "3":
            print("Выход...")
            return True
        else:
            print("Неверный выбор")
            return False

        print(f"Запуск: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        return result.returncode == 0

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        return True
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
