#!/usr/bin/env python3
"""
Скрипт для подготовки проекта к деплою на Railway
"""

import os
import subprocess
import sys

def check_git():
    """Проверяет, инициализирован ли Git репозиторий"""
    try:
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git():
    """Инициализирует Git репозиторий"""
    print("🔧 Инициализация Git репозитория...")
    subprocess.run(['git', 'init'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Initial commit: Telegram System Message Cleaner Bot'])

def create_github_repo():
    """Создает GitHub репозиторий"""
    print("\n📝 Для создания GitHub репозитория:")
    print("1. Перейдите на https://github.com/new")
    print("2. Создайте новый репозиторий")
    print("3. НЕ инициализируйте с README")
    print("4. Скопируйте URL репозитория")
    
    repo_url = input("\nВведите URL вашего GitHub репозитория: ").strip()
    
    if repo_url:
        print("🔗 Подключение к GitHub...")
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url])
        subprocess.run(['git', 'branch', '-M', 'main'])
        subprocess.run(['git', 'push', '-u', 'origin', 'main'])
        print("✅ Код загружен в GitHub!")
        return repo_url
    return None

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        'bot.py',
        'config.py', 
        'requirements.txt',
        'Procfile',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все необходимые файлы найдены!")
    return True

def main():
    print("🚀 Подготовка к деплою на Railway")
    print("=" * 50)
    
    # Проверяем файлы
    if not check_files():
        print("❌ Не все файлы готовы. Проверьте структуру проекта.")
        return
    
    # Проверяем Git
    if not check_git():
        print("🔧 Git репозиторий не найден. Инициализируем...")
        init_git()
    else:
        print("✅ Git репозиторий найден")
    
    # Создаем GitHub репозиторий
    repo_url = create_github_repo()
    
    if repo_url:
        print("\n🎉 Готово! Теперь можете деплоить на Railway:")
        print("\n📋 Инструкция:")
        print("1. Перейдите на https://railway.app")
        print("2. Войдите через GitHub")
        print("3. Нажмите 'New Project'")
        print("4. Выберите 'Deploy from GitHub repo'")
        print("5. Выберите ваш репозиторий")
        print("6. В разделе 'Variables' добавьте BOT_TOKEN")
        print("7. Бот автоматически запустится!")
        
        print(f"\n🔗 Ваш репозиторий: {repo_url}")
    else:
        print("\n⚠️ GitHub репозиторий не был создан.")
        print("Вы можете создать его вручную и загрузить файлы.")

if __name__ == "__main__":
    main() 