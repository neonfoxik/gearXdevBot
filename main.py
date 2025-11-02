import subprocess
import time
import requests
import os
import signal
import sys
import threading
from threading import Thread
import re
import tempfile

# Глобальные переменные для хранения процессов
tuna_process = None
server_process = None
tunnel_url = None


def log_info(message):
    """Логирование информационных сообщений"""
    print(f"ℹ️  [INFO] {message}")


def log_success(message):
    """Логирование успешных операций"""
    print(f"✅ [SUCCESS] {message}")


def log_warning(message):
    """Логирование предупреждений"""
    print(f"⚠️  [WARNING] {message}")


def log_error(message):
    """Логирование ошибок"""
    print(f"❌ [ERROR] {message}")


def log_server(message):
    """Логирование сообщений от сервера"""
    print(f"🐍 [SERVER] {message}")


def log_bot(message):
    """Логирование сообщений от бота"""
    print(f"🤖 [BOT] {message}")


def run_tunnel_background():
    """Запускает туннель в фоновом режиме и возвращает URL"""
    global tuna_process, tunnel_url

    log_info("Запуск туннеля в фоновом режиме...")

    # Создаем временный файл для вывода туннеля
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='_tuna.log') as temp_file:
        temp_filename = temp_file.name

    log_info(f"Логи туннеля записываются в: {temp_filename}")

    try:
        # Запускаем туннель в фоновом режиме
        if sys.platform == "win32":
            tuna_process = subprocess.Popen(
                ['tuna', 'http', '8000'],
                stdout=open(temp_filename, 'w'),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            tuna_process = subprocess.Popen(
                ['tuna', 'http', '8000'],
                stdout=open(temp_filename, 'w'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

        log_info("Туннель запущен в фоновом режиме, ожидание URL...")

        # Ждем появления URL в файле
        url = None
        max_attempts = 30
        attempt = 0

        while attempt < max_attempts and not url:
            time.sleep(2)
            attempt += 1

            if os.path.exists(temp_filename):
                with open(temp_filename, 'r') as f:
                    content = f.read()

                    # Ищем URL в содержимом файла
                    url_patterns = [
                        r'https://[a-zA-Z0-9-]+\.tuna\.pf',
                        r'https://[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.tuna\.pf',
                        r'https://[^\s]+\.tuna\.pf',
                        r'https://[a-zA-Z0-9-]+\.ru\.tuna\.am',
                        r'https://[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.ru\.tuna\.am',
                        r'Forwarding\s+(https://[^\s]+)'
                    ]

                    for pattern in url_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            url = matches[-1] if isinstance(matches[-1], str) else matches[-1][0] if matches[
                                -1] else None
                            if url:
                                break

            log_info(f"Попытка {attempt}/{max_attempts}: ожидание URL туннеля...")

            if url:
                break

        if not url:
            log_error("Не удалось получить URL туннеля")
            if os.path.exists(temp_filename):
                with open(temp_filename, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) >= 10 else lines
                    log_error("Последние строки лога туннеля:")
                    for line in last_lines:
                        print(f"    {line.strip()}")
            return None

        url = url.strip().rstrip('.').rstrip('>').strip()
        tunnel_url = url
        log_success(f"Туннель запущен: {url}")
        return url

    except Exception as e:
        log_error(f"Ошибка при запуске туннеля: {e}")
        return None


def update_env_file(url, env_file='.env'):
    """Обновляет переменную HOOK в .env файле."""
    log_info(f"Обновление {env_file}...")

    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
        log_info(f"Файл {env_file} прочитан, {len(lines)} строк")
    else:
        log_warning(f"Файл {env_file} не существует, будет создан новый")

    found = False
    for i, line in enumerate(lines):
        if line.startswith('HOOK='):
            old_value = line.strip()
            lines[i] = f'HOOK={url}\n'
            found = True
            log_info(f"Обновлена переменная HOOK: {old_value} -> HOOK={url}")
            break

    if not found:
        lines.append(f'HOOK={url}\n')
        log_info(f"Добавлена новая переменная HOOK={url}")

    with open(env_file, 'w') as f:
        f.writelines(lines)

    log_success(f"Файл {env_file} успешно обновлен")


def run_django_server():
    """Запускает Django сервер с выводом логов в реальном времени"""
    global server_process
    log_info("Запуск Django сервера...")

    try:
        python_cmd = 'python3' if sys.platform != "win32" else 'python'

        if sys.platform == "win32":
            server_process = subprocess.Popen(
                [python_cmd, 'manage.py', 'runserver'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            server_process = subprocess.Popen(
                [python_cmd, 'manage.py', 'runserver'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

        log_success("Django сервер запущен")

        def output_reader():
            log_info("Запущен мониторинг логов сервера...")
            while True:
                if server_process is None:
                    break
                line = server_process.stdout.readline()
                if not line and server_process.poll() is not None:
                    log_warning("Сервер завершил работу")
                    break
                if line:
                    # Автоматически определяем бот-запросы и логируем их отдельно
                    line_text = line.strip()
                    if 'bot' in line_text.lower() or 'webhook' in line_text.lower() or 'POST' in line_text:
                        log_bot(line_text)
                    else:
                        log_server(line_text)

        thread = Thread(target=output_reader)
        thread.daemon = True
        thread.start()

    except Exception as e:
        log_error(f"Ошибка при запуске сервера: {e}")


def wait_for_server(timeout=90):
    """Ждем, пока сервер не станет доступен."""
    log_info(f"Ожидание запуска сервера (таймаут: {timeout} сек)...")

    start_time = time.time()
    last_status_time = start_time

    while time.time() - start_time < timeout:
        elapsed = int(time.time() - start_time)

        if time.time() - last_status_time >= 5:
            log_info(f"Проверка сервера... ({elapsed}/{timeout} сек)")
            last_status_time = time.time()

        try:
            response = requests.get('http://127.0.0.1:8000/bot/', timeout=5)
            if response.status_code == 200:
                log_success(f"Сервер готов через {elapsed} сек!")
                return True
            elif response.status_code < 500:
                log_success(f"Сервер отвечает (статус {response.status_code}) через {elapsed} сек!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            log_warning("Таймаут при проверке сервера")
        except Exception as e:
            log_warning(f"Ошибка при проверке сервера: {e}")

        time.sleep(2)

    log_error(f"Сервер не запустился в течение {timeout} секунд")
    return False


def check_tunnel_status():
    """Проверяет статус туннеля"""
    global tunnel_url
    if not tunnel_url:
        return False

    try:
        # Пробуем разные пути, так как корень может не отвечать
        test_paths = ['/', '/webhook/', '/bot/']
        for path in test_paths:
            try:
                test_url = f"{tunnel_url}{path}"
                response = requests.get(test_url, timeout=10)
                if response.status_code < 500:  # Любой ответ кроме 5xx считается успехом
                    return True
            except:
                continue
        return False
    except:
        return False


def stop_processes(signum=None, frame=None):
    """Корректное завершение процессов"""
    log_info("Завершение работы...")
    global tuna_process, server_process

    if server_process:
        log_info("Остановка Django сервера...")
        try:
            if sys.platform == "win32":
                server_process.terminate()
            else:
                server_process.terminate()

            for _ in range(10):
                if server_process.poll() is not None:
                    break
                time.sleep(0.5)
            else:
                log_warning("Принудительное завершение сервера...")
                server_process.kill()

            log_success("Django сервер остановлен")
        except Exception as e:
            log_error(f"Ошибка при остановке сервера: {e}")

    if tuna_process:
        log_info("Остановка туннеля...")
        try:
            if sys.platform == "win32":
                tuna_process.terminate()
            else:
                tuna_process.terminate()

            for _ in range(10):
                if tuna_process.poll() is not None:
                    break
                time.sleep(0.5)
            else:
                log_warning("Принудительное завершение туннеля...")
                tuna_process.kill()

            log_success("Туннель остановлен")
        except Exception as e:
            log_error(f"Ошибка при остановке туннеля: {e}")

    temp_files = [f for f in os.listdir('.') if f.endswith('_tuna.log')]
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            log_info(f"Удален временный файл: {temp_file}")
        except:
            pass

    log_success("Все процессы остановлены. До свидания!")
    sys.exit(0)


def print_status():
    """Периодически выводит статус системы"""

    def status_loop():
        while True:
            time.sleep(30)
            log_info("=== СТАТУС СИСТЕМЫ ===")

            # Проверяем туннель
            tunnel_ok = check_tunnel_status()
            if tunnel_ok:
                log_success(f"Туннель активен: {tunnel_url}")
            else:
                log_warning("Туннель не доступен (это нормально если нет активных подключений)")

            # Проверяем сервер
            server_ok = False
            try:
                response = requests.get('http://127.0.0.1:8000/bot/', timeout=5)
                server_ok = response.status_code == 200
            except:
                pass

            if server_ok:
                log_success("Сервер работает")
            else:
                log_warning("Сервер не отвечает")

            log_info("======================")

    thread = Thread(target=status_loop)
    thread.daemon = True
    thread.start()


def main():
    global tuna_process, server_process, tunnel_url

    signal.signal(signal.SIGINT, stop_processes)

    log_info("🚀 Запуск автоматического развертывания Django проекта")
    log_info(f"📂 Рабочая директория: {os.getcwd()}")

    try:
        # Шаг 1: Запускаем туннель в фоне
        log_info("=" * 60)
        log_info("ШАГ 1: Запуск туннеля")
        tunnel_url = run_tunnel_background()

        if not tunnel_url:
            log_error("Не удалось запустить туннель. Завершение работы.")
            stop_processes()
            return

        # Шаг 2: Обновляем .env файл
        log_info("=" * 60)
        log_info("ШАГ 2: Обновление конфигурации")
        update_env_file(tunnel_url)

        # Шаг 3: Запускаем Django сервер
        log_info("=" * 60)
        log_info("ШАГ 3: Запуск Django приложения")
        run_django_server()

        # Шаг 4: Ждем, пока сервер не будет готов
        log_info("=" * 60)
        log_info("ШАГ 4: Ожидание запуска сервера")
        if not wait_for_server():
            log_error("Сервер не запустился. Завершение работы.")
            stop_processes()
            return

        # Шаг 5: Запускаем мониторинг статуса (без установки вебхука)
        log_info("=" * 60)
        log_info("ШАГ 5: Запуск мониторинга системы")
        log_info("Вебхук не устанавливается автоматически")
        log_info("Для настройки вебхука используйте интерфейс бота")

        print_status()

        # Финальный отчет
        log_info("=" * 60)
        log_info("🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
        log_success(f"🌐 Туннель: {tunnel_url}")
        log_success("🖥️  Сервер: http://127.0.0.1:8000")
        log_success("📊 Панель бота: http://127.0.0.1:8000/bot/")
        log_info("🔗 Вебхук: для настройки используйте интерфейс бота")

        log_info("\n" + "=" * 60)
        log_info("Система работает. Нажмите Ctrl+C для остановки.")
        log_info("Статус системы будет обновляться каждые 30 секунд.")
        log_info("=" * 60)

        while True:
            time.sleep(1)

    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        stop_processes()


if __name__ == "__main__":
    main()