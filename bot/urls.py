from django.conf import settings
from django.urls import path
import logging

from bot import views

# Импортируем views для регистрации обработчиков бота
# Это происходит после полной инициализации Django
_ = views

# Установка вебхука после регистрации всех обработчиков
try:
    if not settings.LOCAL and settings.HOOK and settings.BOT_TOKEN:
        webhook_url = f"{settings.HOOK}/bot/{settings.BOT_TOKEN}"
        views.bot.set_webhook(url=webhook_url)
        logging.info(f'Webhook установлен: {webhook_url}')

        # Проверяем информацию о вебхуке
        webhook_info = views.bot.get_webhook_info()
        logging.info(f'Webhook info: URL={webhook_info.url}, Pending={webhook_info.pending_update_count}')
    elif settings.LOCAL:
        logging.info('Локальный режим - вебхук не устанавливается')
    else:
        logging.warning('HOOK или BOT_TOKEN не установлены в настройках')
except Exception as e:
    logging.error(f"Ошибка при установке вебхука: {e}")

app_name = 'bot'


urlpatterns = [
    path(settings.BOT_TOKEN, views.index, name="index"),
    path('', views.set_webhook, name="set_webhook"),
    path("status/", views.status, name="status"),
]
