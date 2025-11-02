from telebot import types

from bot import bot
from bot.models import User
from bot.texts import START_TEXT
from bot.keyboards import main_markup


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    """Обработчик команды /start с автоматической регистрацией пользователя."""
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
    
    # Отправляем приветственное сообщение
    bot.send_message(
        message.chat.id,
        START_TEXT,
        reply_markup=main_markup
    )
