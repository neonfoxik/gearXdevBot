from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


main_markup = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton("🌐 Наш сайт 🌐", url="https://example.com")
btn2 = InlineKeyboardButton("⭐Наши отзывы ⭐", url="https://t.me/GearXdevGroup")
btn3 = InlineKeyboardButton("📝 Заказать айт или бота", url="https://t.me/GearXdev")
main_markup.add(btn1).add(btn2).add(btn3)

