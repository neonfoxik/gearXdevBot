#!/usr/bin/env python
"""
Скрипт для диагностики проблем с ботом
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dd.settings')
django.setup()

from django.conf import settings
from bot import bot
from telebot import logger

def check_settings():
    """Проверка настроек"""
    print("=== ПРОВЕРКА НАСТРОЕК ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"LOCAL: {settings.LOCAL}")
    print(f"HOOK: {settings.HOOK}")
    print(f"BOT_TOKEN: {'***' + settings.BOT_TOKEN[-10:] if settings.BOT_TOKEN else 'None'}")
    print(f"OWNER_ID: {settings.OWNER_ID}")
    print()

def check_database():
    """Проверка подключения к БД"""
    print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Подключение к БД успешно")

        # Проверяем модель User
        from bot.models import User
        user_count = User.objects.count()
        print(f"✅ Модель User доступна, пользователей: {user_count}")

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
    print()

def check_bot():
    """Проверка бота"""
    print("=== ПРОВЕРКА БОТА ===")
    try:
        bot_info = bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username} (ID: {bot_info.id})")
        print(f"   ✅ Можно ли присоединяться к группам: {bot_info.can_join_groups}")
        print(f"   ✅ Поддержка inline: {bot_info.supports_inline_queries}")

        # Проверяем количество зарегистрированных обработчиков
        handlers_count = len(bot.message_handlers) + len(bot.callback_query_handlers)
        print(f"   ✅ Зарегистрировано обработчиков: {handlers_count}")

        # Проверяем наличие обработчика /start
        start_handlers = [h for h in bot.message_handlers if hasattr(h, 'commands') and 'start' in h.commands]
        print(f"   ✅ Обработчик /start: {'найден' if start_handlers else 'не найден'}")

    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
    print()

def check_webhook():
    """Проверка вебхука"""
    print("=== ПРОВЕРКА ВЕБХУКА ===")
    try:
        webhook_info = bot.get_webhook_info()
        print(f"URL: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        if webhook_info.url:
            print("✅ Вебхук установлен")
        else:
            print("⚠️  Вебхук не установлен")
    except Exception as e:
        print(f"❌ Ошибка проверки вебхука: {e}")
    print()

if __name__ == "__main__":
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМ С БОТОМ")
    print("=" * 50)

    check_settings()
    check_database()
    check_bot()
    check_webhook()

    print("=== РЕЗУЛЬТАТЫ ===")
    if settings.LOCAL:
        print("⚠️  Локальный режим - бот работает через polling, вебхук игнорируется")
    else:
        print("📡 Production режим - бот работает через вебхук")
