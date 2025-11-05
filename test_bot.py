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
        # Исправляем URL - убираем дублирование /bot/
        base_url = settings.HOOK.rstrip('/')
        if base_url.endswith('/bot'):
            status_url = f"{base_url}/status/"
        else:
            status_url = f"{base_url}/bot/status/"

        print(f"📡 Тестируем URL: {status_url}")

        # Сначала пробуем HTTPS с отключенной проверкой SSL
        try:
            response = requests.get(status_url, timeout=10, verify=False)
            print(f"📡 HTTPS статус endpoint: {response.status_code}")

            if response.status_code == 200:
                print("✅ Webhook endpoint доступен по HTTPS")
                return
            else:
                print(f"⚠️ HTTPS вернул код {response.status_code}")

        except requests.exceptions.SSLError as ssl_error:
            print(f"❌ SSL ошибка: {ssl_error}")
            print("🔄 Пробуем HTTP...")

        # Если HTTPS не работает, пробуем HTTP
        try:
            http_url = status_url.replace('https://', 'http://')
            print(f"📡 Пробуем HTTP: {http_url}")
            response = requests.get(http_url, timeout=10)
            print(f"📡 HTTP статус endpoint: {response.status_code}")

            if response.status_code == 200:
                print("✅ Webhook endpoint доступен по HTTP")
                print("💡 Рекомендуется настроить HTTPS для production")
            else:
                print(f"❌ HTTP endpoint вернул код {response.status_code}")

        except requests.exceptions.RequestException as http_error:
            print(f"❌ Ошибка подключения по HTTP: {http_error}")
            print("🔍 Проверьте настройки nginx и домена")

if __name__ == "__main__":
    test_bot_response()
    test_webhook_endpoint()

    print("\n" + "="*50)
    print("📋 ИНСТРУКЦИИ:")
    print("1. Запустите этот скрипт на сервере")
    print("2. Проверьте логи Django сервера")
    print("3. Отправьте команду /start боту в Telegram")
    print("4. Посмотрите логи - должны быть сообщения о получении обновления")
