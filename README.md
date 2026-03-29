🤖 AmneziaWG & MTProto Management BotПрофессиональный Telegram-бот для управления личным VPN-сервером. Разработан для автоматизации рутины системного администратора: создание юзеров, мониторинг ресурсов и оповещение о сбоях.🛠 ФункционалVPN Control: Генерация конфигов (.conf) и QR-кодов для AmneziaWG.Auto-Stats: Ежедневные отчеты по трафику с автоматическим сбросом счетчиков.Server Health: Мониторинг CPU, RAM и Disk (с защитой от переполнения логами).Watchdog: Проверка Docker-контейнера каждые 10 минут (алерт админу при падении).MTProto: Встроенная поддержка прокси для Telegram.🚀 Быстрый зарт (Ubuntu/Debian)1. Подготовка окружения# Создаем рабочую директорию
sudo mkdir -p /opt/amnezia_bot && cd /opt/amnezia_bot

# Устанавливаем системные зависимости
sudo apt update && sudo apt install -y python3-pip python3-venv docker.io openssl

# Настраиваем виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install aiogram apscheduler pytz segno python-dotenv
2. Настройка переменных (.env)Создайте файл .env в корне папки:nano .env
Вставьте и отредактируйте данные:BOT_TOKEN=8691355686:AAFWX...  # Токен от BotFather
ADMIN_ID=892882951             # Твой Telegram ID
SERVER_IP=1.2.3.4              # IP твоего сервера
PROXY_SECRET=24887842a...      # Секрет для MTProto
CONTAINER_NAME=amnezia_container
3. Настройка автозагрузки (Systemd)Чтобы бот работал после перезагрузки сервера:sudo nano /etc/systemd/system/amnezia_bot.service
Вставьте содержимое:[Unit]
Description=AmneziaWG Telegram Bot
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/amnezia_bot
ExecStart=/opt/amnezia_bot/venv/bin/python3 /opt/amnezia_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Запуск:sudo systemctl daemon-reload
sudo systemctl enable --now amnezia_bot
🧹 Обслуживание сервераЕсли бот сигнализирует о заполнении диска (Disk > 80%):# Очистка системных логов старше 2 дней
sudo journalctl --vacuum-time=2d

# Очистка кэша пакетов
sudo apt-get clean

# Удаление неиспользуемых данных Docker
docker system prune -f
📂 Структура проектаmain.py — основной код бота..env — конфиденциальные данные (игнорируется Git)..gitignore — список исключений для Git.README.md — эта инструкция.
### Что сделать дальше?
1. Создай файл на сервере: `nano README.md`.
2. Вставь текст выше и сохрани.
3. Добавь его в Git:
   ```bash
   git add README.md
   git commit -m "Add professional README"
   git push origin main
🤖 AmneziaWG & MTProto Management BotПрофессиональный Telegram-бот для управления личным VPN-сервером. Разработан для автоматизации рутины системного администратора: создание юзеров, мониторинг ресурсов и оповещение о сбоях.🛠 ФункционалVPN Control: Генерация конфигов (.conf) и QR-кодов для AmneziaWG.Auto-Stats: Ежедневные отчеты по трафику с автоматическим сбросом счетчиков.Server Health: Мониторинг CPU, RAM и Disk (с защитой от переполнения логами).Watchdog: Проверка Docker-контейнера каждые 10 минут (алерт админу при падении).MTProto: Встроенная поддержка прокси для Telegram.🚀 Быстрый зарт (Ubuntu/Debian)1. Подготовка окружения# Создаем рабочую директорию
sudo mkdir -p /opt/amnezia_bot && cd /opt/amnezia_bot

# Устанавливаем системные зависимости
sudo apt update && sudo apt install -y python3-pip python3-venv docker.io openssl

# Настраиваем виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install aiogram apscheduler pytz segno python-dotenv
2. Настройка переменных (.env)Создайте файл .env в корне папки:nano .env
Вставьте и отредактируйте данные:BOT_TOKEN=8691355686:AAFWX...  # Токен от BotFather
ADMIN_ID=892882951             # Твой Telegram ID
SERVER_IP=1.2.3.4              # IP твоего сервера
PROXY_SECRET=24887842a...      # Секрет для MTProto
CONTAINER_NAME=amnezia_container
3. Настройка автозагрузки (Systemd)Чтобы бот работал после перезагрузки сервера:sudo nano /etc/systemd/system/amnezia_bot.service
Вставьте содержимое:[Unit]
Description=AmneziaWG Telegram Bot
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/amnezia_bot
ExecStart=/opt/amnezia_bot/venv/bin/python3 /opt/amnezia_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Запуск:sudo systemctl daemon-reload
sudo systemctl enable --now amnezia_bot
🧹 Обслуживание сервераЕсли бот сигнализирует о заполнении диска (Disk > 80%):# Очистка системных логов старше 2 дней
sudo journalctl --vacuum-time=2d

# Очистка кэша пакетов
sudo apt-get clean

# Удаление неиспользуемых данных Docker
docker system prune -f
📂 Структура проектаmain.py — основной код бота..env — конфиденциальные данные (игнорируется Git)..gitignore — список исключений для Git.README.md — эта инструкция.
### Что сделать дальше?
1. Создай файл на сервере: `nano README.md`.
2. Вставь текст выше и сохрани.
3. Добавь его в Git:
   ```bash
   git add README.md
   git commit -m "Add professional README"
   git push origin main
