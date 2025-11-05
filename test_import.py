#!/usr/bin/env python
"""
Тест импорта для проверки отсутствия циклических зависимостей
"""
import os
import sys

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dd.settings')

try:
    import django
    django.setup()
    print("✅ Django настроен успешно")
except Exception as e:
    print(f"❌ Ошибка настройки Django: {e}")
    sys.exit(1)

try:
    # Импорт bot модуля
    from bot import bot
    print("✅ Бот импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта бота: {e}")
    sys.exit(1)

try:
    # Импорт views
    from bot import views
    print("✅ Views импортированы успешно")
except Exception as e:
    print(f"❌ Ошибка импорта views: {e}")
    sys.exit(1)

try:
    # Импорт моделей
    from bot.models import User
    print("✅ Модели импортированы успешно")
except Exception as e:
    print(f"❌ Ошибка импорта моделей: {e}")
    sys.exit(1)

try:
    # Проверка подключения к БД
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ База данных доступна")
except Exception as e:
    print(f"❌ Ошибка подключения к БД: {e}")
    sys.exit(1)

print("\n🎉 Все импорты прошли успешно! Циклические зависимости исправлены.")
