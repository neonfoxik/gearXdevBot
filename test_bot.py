#!/usr/bin/env python
"""
Тест бота - отправка команды /start самому себе
"""
import os
import sys
import django
import requests
from time import sleep

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dd.settings')
django.setup()

from django.conf import settings
from bot import bot

def test_bot_response():
    """Тестируем ответ бота на команду /start"""
    print("=== ТЕСТИРОВАНИЕ БОТА ===")

    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен")
        return

    try:
        # Получаем информацию о боте
        bot_info = bot.get_me()
        print(f"✅ Бот: @{bot_info.username} (ID: {bot_info.id})")

        # Отправляем команду /start самому себе (если указан OWNER_ID)
        if settings.OWNER_ID:
            print(f"📤 Отправка команды /start пользователю {settings.OWNER_ID}...")

            try:
                bot.send_message(settings.OWNER_ID, "/start")
                print("✅ Команда /start отправлена")
                print("🔍 Проверьте, получил ли бот команду в логах сервера")
            except Exception as e:
                print(f"❌ Ошибка отправки команды: {e}")
        else:
            print("⚠️  OWNER_ID не установлен, невозможно протестировать отправку команды")

        # Проверяем вебхук
        webhook_info = bot.get_webhook_info()
        print(f"📡 Вебхук URL: {webhook_info.url}")
        print(f"📡 Ожидающие обновления: {webhook_info.pending_update_count}")

        if webhook_info.pending_update_count > 0:
            print("⚠️  Есть ожидающие обновления - бот может не отвечать на новые команды")

    except Exception as e:
        print(f"❌ Ошибка тестирования бота: {e}")

def test_webhook_endpoint():
    """Тестируем доступность webhook endpoint"""
    print("\n=== ТЕСТИРОВАНИЕ WEBHOOK ENDPOINT ===")

    if not settings.HOOK:
        print("❌ HOOK не установлен")
        return

    webhook_url = f"{settings.HOOK}/bot/{settings.BOT_TOKEN}"

    try:
        # Тестируем GET запрос
        response = requests.get(f"{settings.HOOK}/bot/status/", timeout=10)
        print(f"📡 Статус endpoint: {response.status_code}")

        if response.status_code == 200:
            print("✅ Webhook endpoint доступен")
        else:
            print(f"❌ Webhook endpoint вернул код {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к webhook endpoint: {e}")

if __name__ == "__main__":
    test_bot_response()
    test_webhook_endpoint()

    print("\n" + "="*50)
    print("📋 ИНСТРУКЦИИ:")
    print("1. Запустите этот скрипт на сервере")
    print("2. Проверьте логи Django сервера")
    print("3. Отправьте команду /start боту в Telegram")
    print("4. Посмотрите логи - должны быть сообщения о получении обновления")
