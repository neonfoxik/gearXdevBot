# 🚀 Развертывание GearX DevBot на VPS сервере

Подробная инструкция по запуску Django приложения с Telegram ботом в Docker на VPS сервере.

## 📋 Предварительные требования

- VPS сервер с Ubuntu/Debian/CentOS
- Docker и Docker Compose установлены
- Доменное имя (опционально, но рекомендуется)
- SSL сертификат (опционально, но рекомендуется для production)

## 🛠️ Установка Docker и Docker Compose

### Ubuntu/Debian:
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавляем ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагружаемся
newgrp docker
```

### CentOS/RHEL:
```bash
# Устанавливаем Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запускаем и включаем Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

## 📁 Подготовка проекта

1. **Загрузите проект на сервер:**
```bash
# Клонируйте репозиторий или загрузите файлы
git clone <your-repo-url> gearxdevbot
cd gearxdevbot
```

2. **Создайте файл переменных окружения:**
```bash
cp env.example .env
```

3. **Отредактируйте .env файл:**
```bash
nano .env
```

Заполните следующие переменные:
```env
# Django настройки
DEBUG=False
SECRET_KEY=ваш-супер-секретный-ключ-здесь
ALLOWED_HOSTS=ваш-домен.com,localhost,127.0.0.1

# База данных PostgreSQL
POSTGRES_DB=gearxdevbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ваш-сильный-пароль-для-postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Telegram Bot настройки
BOT_TOKEN=ваш-telegram-bot-token
OWNER_ID=ваш-telegram-user-id

# Webhook URL
HOOK=https://ваш-домен.com/bot/

# Локальная разработка
LOCAL=False
```

## 🔐 Настройка SSL (опционально, но рекомендуется)

### Использование Let's Encrypt (бесплатно):

1. **Установите Certbot:**
```bash
sudo apt install -y certbot
```

2. **Получите SSL сертификат:**
```bash
sudo certbot certonly --standalone -d ваш-домен.com
```

3. **Создайте директорию для SSL:**
```bash
mkdir ssl
sudo cp /etc/letsencrypt/live/ваш-домен.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/ваш-домен.com/privkey.pem ssl/
```

4. **Раскомментируйте HTTPS сервер в nginx.conf**

## 🚀 Запуск приложения

### 1. Постройте и запустите контейнеры:
```bash
# Постройте образы
docker-compose build

# Запустите в фоне
docker-compose up -d
```

### 2. Проверьте статус:
```bash
# Проверьте запущенные контейнеры
docker-compose ps

# Посмотрите логи
docker-compose logs -f web
```

### 3. Проверьте работу:
- **Django приложение:** `http://ваш-домен.com` или `http://IP-адрес-сервера`
- **Админ панель бота:** `http://ваш-домен.com/bot/`
- **PostgreSQL:** доступен на порту 5432 (только внутри Docker сети)

## 🔧 Управление приложением

### Просмотр логов:
```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs web
docker-compose logs db
docker-compose logs nginx

# Следить за логами в реальном времени
docker-compose logs -f web
```

### Остановка и перезапуск:
```bash
# Остановить все сервисы
docker-compose down

# Перезапустить
docker-compose restart

# Перезапустить конкретный сервис
docker-compose restart web
```

### Обновление приложения:
```bash
# Остановить
docker-compose down

# Получить обновления
git pull

# Перестроить образы
docker-compose build --no-cache

# Запустить
docker-compose up -d
```

## 📊 Мониторинг и отладка

### Проверка здоровья:
```bash
# Проверить все контейнеры
docker ps

# Проверить использование ресурсов
docker stats

# Войти в контейнер приложения
docker-compose exec web bash

# Проверить базу данных
docker-compose exec db psql -U postgres -d gearxdevbot
```

### Резервное копирование базы данных:
```bash
# Создать бэкап
docker-compose exec db pg_dump -U postgres gearxdevbot > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из бэкапа
docker-compose exec -T db psql -U postgres -d gearxdevbot < backup_file.sql
```

## ⚠️ Устранение неполадок

### Приложение не запускается:
1. Проверьте логи: `docker-compose logs web`
2. Проверьте переменные окружения в `.env`
3. Убедитесь что база данных готова: `docker-compose logs db`

### Nginx возвращает ошибку 502:
1. Проверьте что Django приложение работает: `docker-compose logs web`
2. Проверьте конфигурацию nginx: `docker-compose exec nginx nginx -t`

### Проблемы с базой данных:
1. Проверьте подключение: `docker-compose logs db`
2. Проверьте переменные окружения PostgreSQL
3. Попробуйте пересоздать базу: `docker-compose down -v` и `docker-compose up -d`

### Telegram бот не отвечает:
1. Проверьте BOT_TOKEN в `.env`
2. Проверьте webhook URL в админ панели бота
3. Проверьте логи Django приложения

## 🔒 Безопасность

### Важные меры безопасности:
1. **Измените SECRET_KEY** в `.env` файле
2. **Используйте сильные пароли** для PostgreSQL
3. **Ограничьте доступ** к порту 5432 (не открывайте его наружу)
4. **Включите SSL/TLS** для HTTPS
5. **Регулярно обновляйте** Docker образы
6. **Настройте firewall** (UFW, firewalld)

### Настройка firewall (Ubuntu):
```bash
# Включить UFW
sudo ufw enable

# Разрешить SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Проверить статус
sudo ufw status
```

## 📈 Оптимизация производительности

### Настройка PostgreSQL:
Отредактируйте `docker-compose.yml` и добавьте настройки PostgreSQL:
```yaml
db:
  image: postgres:15
  environment:
    POSTGRES_DB: gearxdevbot
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_SHARED_BUFFERS: 256MB
    POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
    POSTGRES_WORK_MEM: 4MB
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./postgresql.conf:/etc/postgresql/postgresql.conf
  command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

### Настройка Nginx:
Отрегулируйте `nginx.conf` для лучшей производительности:
- Увеличьте `worker_connections`
- Настройте кэширование статических файлов
- Включите gzip сжатие

## 🔄 Автоматические обновления

### Настройка автоматического перезапуска:
```yaml
# В docker-compose.yml добавьте
services:
  web:
    restart: unless-stopped
  db:
    restart: unless-stopped
  nginx:
    restart: unless-stopped
```

### Cron для автоматических обновлений:
```bash
# Создайте скрипт обновления
cat > update_app.sh << 'EOF'
#!/bin/bash
cd /path/to/your/app
docker-compose pull
docker-compose up -d --build
EOF

chmod +x update_app.sh

# Добавьте в crontab (ежедневно в 2:00)
0 2 * * * /path/to/update_app.sh
```

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи всех сервисов
2. Убедитесь что все переменные окружения правильно настроены
3. Проверьте сетевые настройки и firewall
4. Убедитесь что порты не заняты другими приложениями

---

**Примечание:** Эта инструкция предполагает использование доменного имени. Если у вас нет домена, замените `ваш-домен.com` на IP-адрес вашего VPS сервера.
