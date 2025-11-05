from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


main_markup = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton("🌐 Сайт 🌐", url="https://example.com")
btn2 = InlineKeyboardButton("⭐ Отзывы ⭐", url="https://t.me/+axs4h63V921jYWFh")
btn3 = InlineKeyboardButton("📝 Заказать", url="https://t.me/GearXdev")
main_markup.add(btn1).add(btn2).add(btn3)

