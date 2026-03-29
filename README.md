# 🤖 AmneziaWG & MTProto Management Bot

Профессиональный Telegram-бот для управления личным VPN-сервером. Разработан для автоматизации рутины системного администратора.

---

## 🛠 Основной функционал

* **VPN Control:** Генерация конфигов (.conf) и QR-кодов для AmneziaWG.
* **Auto-Stats:** Ежедневные отчеты по трафику с автоматическим сбросом счетчиков.
* **Server Health:** Мониторинг CPU, RAM и Disk (защита от переполнения логами).
* **Watchdog:** Проверка Docker-контейнеров каждые 10 минут.
* **MTProto:** Поддержка прокси для Telegram внутри бота.

---

## 🚀 Быстрый старт (Ubuntu/Debian)

### 1. Подготовка окружения
```bash
# Создаем рабочую директорию
sudo mkdir -p /opt/amnezia_bot && cd /opt/amnezia_bot

# Устанавливаем системные зависимости
sudo apt update && sudo apt install -y python3-pip python3-venv docker.io openssl
2. Настройка виртуального окружения
Bash
python3 -m venv venv
source venv/bin/activate
pip install aiogram apscheduler pytz segno python-dotenv
3. Настройка переменных (.env)
Создайте файл .env и добавьте ваши данные:

BOT_TOKEN (от BotFather)

ADMIN_ID (ваш ID)

SERVER_IP (IP вашего сервера)

🧹 Обслуживание сервера
Если диск заполнен (Disk > 80%):

Очистка журналов: sudo journalctl --vacuum-time=2d

Очистка Docker: docker system prune -f

📜 Автозагрузка (Systemd)
Чтобы бот работал после перезагрузки:

Ini, TOML
[Service]
ExecStart=/opt/amnezia_bot/venv/bin/python3 /opt/amnezia_bot/main.py
Restart=always


