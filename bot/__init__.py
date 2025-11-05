# Этот файл нужен для корректной работы пакета bot
import logging
import telebot

from django.conf import settings

bot = telebot.TeleBot(
    settings.BOT_TOKEN,
    threaded=False,
    skip_pending=True,
)

# Установка вебхука при запуске (только если не в локальном режиме)
try:
    if not settings.LOCAL and settings.HOOK and settings.BOT_TOKEN:
        webhook_url = f"{settings.HOOK}/bot/{settings.BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        logging.info(f'Webhook установлен: {webhook_url}')
    elif settings.LOCAL:
        logging.info('Локальный режим - вебхук не устанавливается')
    else:
        logging.warning('HOOK или BOT_TOKEN не установлены в настройках')
except Exception as e:
    logging.error(f"Ошибка при установке вебхука: {e}")

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