#!/bin/bash

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
while ! pg_isready -h db -p 5432 -U postgres; do
  echo "База данных не готова, ждем..."
  sleep 2
done
echo "База данных готова!"

# Установка правильных прав на директории (выполняется от root)
echo "Установка прав на директории..."
mkdir -p static media
chmod -R 755 static media
chown -R app:app static media

# Переключаемся на пользователя app для выполнения python команд
su app -c "
# Применение миграций
echo 'Применение миграций базы данных...'
python manage.py migrate

# Сбор статических файлов
echo 'Сбор статических файлов...'
python manage.py collectstatic --noinput

# Проверка импортов перед запуском сервера
echo 'Проверка импортов...'
python test_import.py

# Проверка бота перед запуском сервера
echo 'Проверка конфигурации бота...'
python debug_bot.py

# Тестирование бота
echo 'Тестирование бота...'
python test_bot.py

# Запуск сервера
echo 'Запуск Django сервера...'
exec python manage.py runserver 0.0.0.0:8000
"
