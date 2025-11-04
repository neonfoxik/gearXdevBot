#!/bin/bash

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
while ! nc -z db 5432; do
  sleep 1
done
echo "База данных готова!"

# Применение миграций
echo "Применение миграций базы данных..."
python manage.py migrate

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Запуск сервера
echo "Запуск Django сервера..."
exec python manage.py runserver 0.0.0.0:8000
