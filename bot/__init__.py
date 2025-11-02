# Этот файл нужен для корректной работы пакета bot
import logging
import telebot

from django.conf import settings

bot = telebot.TeleBot(
    settings.BOT_TOKEN,
    threaded=False,
    skip_pending=True,
)

# Отправка сообщения при старте
try:
    bot_info = bot.get_me()
    logging.info(f'@{bot_info.username} started')
    if settings.OWNER_ID:
        bot.send_message(settings.OWNER_ID, f"Бот @{bot_info.username} успешно запущен!")
except Exception as e:
    logging.error(f"Ошибка при отправке сообщения при старте: {e}")

logger = telebot.logger
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, filename="ai_log.log", filemode="w")