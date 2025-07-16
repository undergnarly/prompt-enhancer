#!/usr/bin/env python3
"""
Скрипт для запуска тестов Telegram Prompt Enhancer Bot
"""

import sys
import os
import subprocess

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов Telegram Prompt Enhancer Bot...")
    
    # Проверяем наличие pytest
    try:
        import pytest
    except ImportError:
        print("❌ pytest не установлен. Установите: pip install pytest pytest-asyncio")
        return False
    
    # Запускаем тесты
    test_args = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(test_args, check=True)
        print("✅ Все тесты прошли успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Тесты завершились с ошибками (код: {e.returncode})")
        return False


def run_specific_test(test_file):
    """Запуск конкретного теста"""
    print(f"🧪 Запуск теста: {test_file}")
    
    test_args = [
        "pytest",
        f"tests/{test_file}",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(test_args, check=True)
        print("✅ Тест прошел успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Тест завершился с ошибками (код: {e.returncode})")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Запуск конкретного теста
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Запуск всех тестов
        success = run_tests()
    
    sys.exit(0 if success else 1) 