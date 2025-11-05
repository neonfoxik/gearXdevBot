from traceback import format_exc

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from telebot.apihelper import ApiTelegramException
from telebot.types import Update
from telebot import types

from bot import bot
from telebot import logger
from bot.texts import START_TEXT
from bot.keyboards import main_markup

# Логируем регистрацию обработчиков
logger.info("Регистрация обработчиков команд бота...")
logger.info("Обработчик /start зарегистрирован")


@require_GET
def set_webhook(request: HttpRequest) -> JsonResponse:
    """Setting webhook."""
    bot.set_webhook(url=f"{settings.HOOK}/bot/{settings.BOT_TOKEN}")
    if settings.OWNER_ID:
        bot.send_message(settings.OWNER_ID, "Webhook установлен")
    return JsonResponse({"message": "OK"}, status=200)


@require_GET
def status(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "OK"}, status=200)


@csrf_exempt
@require_POST
@sync_to_async
def index(request: HttpRequest) -> JsonResponse:
    if request.META.get("CONTENT_TYPE") != "application/json":
        return JsonResponse({"message": "Bad Request"}, status=403)

    json_string = request.body.decode("utf-8")
    update = Update.de_json(json_string)

    logger.info(f"Получено обновление от Telegram: {update.update_id}")

    # Логируем тип обновления
    if update.message:
        logger.info(f"Сообщение от {update.message.from_user.id}: {update.message.text}")
    elif update.callback_query:
        logger.info(f"Callback от {update.callback_query.from_user.id}: {update.callback_query.data}")

    try:
        bot.process_new_updates([update])
        logger.info("Обновление обработано успешно")
    except ApiTelegramException as e:
        logger.error(f"Telegram exception. {e} {format_exc()}")
    except ConnectionError as e:
        logger.error(f"Connection error. {e} {format_exc()}")
    except Exception as e:
        if settings.OWNER_ID:
            bot.send_message(settings.OWNER_ID, f'Error from index: {e}')
        logger.error(f"Unhandled exception. {e} {format_exc()}")
    return JsonResponse({"message": "OK"}, status=200)


# Bot message handlers
@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    """Обработчик команды /start с автоматической регистрацией пользователя."""
    from bot.models import User

    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")

    user_id = str(message.from_user.id)
    username = message.from_user.username or "none"
    first_name = message.from_user.first_name or "Пользователь"

    # Проверяем, существует ли пользователь
    user, created = User.objects.get_or_create(
        telegram_id=user_id,
        defaults={
            'user_tg_name': username,
            'user_name': first_name,
            'is_admin': False,
        }
    )

    # Если пользователь уже существовал, обновляем его данные
    if not created:
        user.user_tg_name = username
        user.user_name = first_name
        user.save()

    logger.info(f"Пользователь {user_id} {'создан' if created else 'обновлен'}")

    # Отправляем приветственное сообщение
    try:
        bot.send_message(
            message.chat.id,
            START_TEXT,
            reply_markup=main_markup
        )
        logger.info(f"Приветственное сообщение отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")


# Bot callback handlers
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call: types.CallbackQuery):
    """Обработчик проверки подписки."""
    bot.answer_callback_query(call.id, "Функция проверки подписки пока не реализована")


@bot.callback_query_handler(func=lambda call: call.data == "coins_trade")
def coins_trade_callback(call: types.CallbackQuery):
    """Обработчик обмена монет."""
    bot.answer_callback_query(call.id, "Функция обмена монет пока не реализована")


@bot.callback_query_handler(func=lambda call: call.data == "events_menu")
def events_menu_callback(call: types.CallbackQuery):
    """Обработчик меню евентов."""
    bot.answer_callback_query(call.id, "Меню евентов пока не реализовано")


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu_callback(call: types.CallbackQuery):
    """Обработчик возврата в главное меню."""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=START_TEXT,
        reply_markup=main_markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_referal_link")
def get_referal_link_callback(call: types.CallbackQuery):
    """Обработчик получения реферальной ссылки."""
    bot.answer_callback_query(call.id, "Функция реферальных ссылок пока не реализована")


@bot.callback_query_handler(func=lambda call: call.data == "main_video_menu")
def main_video_menu_callback(call: types.CallbackQuery):
    """Обработчик возврата в видео меню."""
    bot.answer_callback_query(call.id, "Видео меню пока не реализовано")


@bot.callback_query_handler(func=lambda call: call.data == "newsletter")
def newsletter_callback(call: types.CallbackQuery):
    """Обработчик рассылки (только для админов)."""
    from bot.models import User

    user_id = str(call.from_user.id)
    try:
        user = User.objects.get(telegram_id=user_id)
        if user.is_admin:
            bot.answer_callback_query(call.id, "Функция рассылки пока не реализована")
        else:
            bot.answer_callback_query(call.id, "У вас нет прав для выполнения этой команды")
    except User.DoesNotExist:
        bot.answer_callback_query(call.id, "Пользователь не найден")
