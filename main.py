import logging, subprocess, os, segno, asyncio, re, pytz
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ ---
API_TOKEN = '8690120988:AAGRMVcObs0cjKOTKvIHYtSgMFcgQbhX5-4'
ADMIN_ID = 892882951
CONTAINER_NAME = "amnezia_container"
TIMEZONE = pytz.timezone('Europe/Moscow')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

class Form(StatesGroup):
    waiting_for_add = State()
    waiting_for_delete = State()
    waiting_for_time = State()

def is_valid_name(name):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))

def get_kb():
    buttons = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🖥 Статус сервера")],
        [KeyboardButton(text="👥 Список юзеров"), KeyboardButton(text="➕ Создать юзера")],
        [KeyboardButton(text="⚙️ Настроить время"), KeyboardButton(text="🔄 Обновить конфиги")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- ЛОГИКА МОНИТОРИНГА И СТАТУСА ---
async def check_container_health():
    """Проверка контейнера раз в 10 минут. Если упал — спам админу."""
    try:
        cmd = f"docker inspect -f '{{{{.State.Running}}}}' {CONTAINER_NAME}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if "true" not in res.stdout.lower():
            await bot.send_message(ADMIN_ID, f"⚠️ **ВНИМАНИЕ!** Контейнер `{CONTAINER_NAME}` **УПАЛ**! VPN недоступен.")
    except Exception as e:
        logging.error(f"Ошибка Watchdog: {e}")

async def get_system_info():
    """Сбор данных о нагрузке на железо"""
    try:
        cpu = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'", shell=True, capture_output=True, text=True).stdout.strip()
        ram = subprocess.run("free -m | awk '/Mem:/ { printf(\"%.2f%% (%.0f/%.0f MB)\", $3/$2*100, $3, $2) }'", shell=True, capture_output=True, text=True).stdout.strip()
        disk = subprocess.run("df -h / | awk 'NR==2 {print $5 \" (\" $4 \" свободно)\"}'", shell=True, capture_output=True, text=True).stdout.strip()
        status_cmd = f"docker inspect -f '{{{{.State.Status}}}}' {CONTAINER_NAME}"
        status = subprocess.run(status_cmd, shell=True, capture_output=True, text=True).stdout.strip()
        return (f"🖥 **Статус сервера:**\n\n📦 Контейнер: `{status}`\n📊 CPU: `{cpu}%` | RAM: `{ram}`\n💾 Диск: `{disk}`")
    except: return "❌ Ошибка получения данных системы."

# --- ЛОГИКА ТРАФИКА (ИСПРАВЛЕННАЯ) ---
async def get_traffic_report():
    try:
        cmd_map = f"docker exec {CONTAINER_NAME} sh -c 'for f in *.conf; do echo \"$f|$(grep PrivateKey \"$f\" | cut -d \" \" -f 3)\"; done'"
        res_map = subprocess.run(cmd_map, shell=True, capture_output=True, text=True, errors='replace')
        key_to_name = {}
        for line in res_map.stdout.strip().split('\n'):
            if '|' in line:
                fname, priv_key = line.split('|')
                if priv_key:
                    gen_pub = subprocess.run(f"echo '{priv_key}' | docker exec -i {CONTAINER_NAME} awg pubkey", shell=True, capture_output=True, text=True).stdout.strip()
                    key_to_name[gen_pub] = fname.replace('.conf', '')

        cmd_stats = f"docker exec {CONTAINER_NAME} awg show all dump"
        res_stats = subprocess.run(cmd_stats, shell=True, capture_output=True, text=True, errors='replace')
        lines = res_stats.stdout.strip().split('\n')
        if not lines or len(lines) < 2: return "📭 Активных сессий нет."
        
        report = "📊 **Активность пользователей:**\n\n"
        found = False
        for line in lines:
            parts = line.split('\t')
            if len(parts) < 8: continue
            pub_key, endpoint = parts[1], parts[3]
            rx_raw, tx_raw = int(parts[6]), int(parts[7])
            if (rx_raw + tx_raw) < 104857: continue 
            
            rx, tx = round(rx_raw/(1024**2), 2), round(tx_raw/(1024**2), 2)
            user_label = key_to_name.get(pub_key, f"Ключ `..{pub_key[:6]}`")
            user_ip = endpoint.split(':')[0] if ':' in endpoint and endpoint != '(none)' else "Не в сети"
            report += f"👤 **{user_label}**\n🌐 IP: `{user_ip}`\n📥 In: {rx} MB | 📤 Out: {tx} MB\n\n"
            found = True
        return report if found else "📭 Активность не обнаружена."
    except Exception as e: return f"❌ Ошибка: {e}"

async def send_daily_report():
    text = await get_traffic_report()
    await bot.send_message(ADMIN_ID, f"⏰ **Ежедневный отчет (Статистика сброшена):**\n{text}", parse_mode="Markdown")
    subprocess.run(f"docker exec {CONTAINER_NAME} awgstart", shell=True)

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        await m.answer("Система мониторинга и управления AmneziaWG активна.", reply_markup=get_kb())

@dp.message(F.text.contains("Статус сервера"))
async def stat_srv(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        await m.answer(await get_system_info(), parse_mode="Markdown")

@dp.message(F.text.contains("Статистика"))
async def manual_stats(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        await m.answer(await get_traffic_report(), parse_mode="Markdown")

@dp.message(F.text.contains("Настроить время"))
async def ask_time(m: types.Message, state: FSMContext):
    if m.from_user.id == ADMIN_ID:
        await m.answer("Введите время отчета по Москве (ЧЧ:ММ):")
        await state.set_state(Form.waiting_for_time)

@dp.message(Form.waiting_for_time)
async def set_time(m: types.Message, state: FSMContext):
    time_match = re.match(r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$", m.text.strip())
    if not time_match:
        await m.answer("❌ Формат ЧЧ:ММ!")
        return
    hh, mm = time_match.groups()
    await state.clear()
    scheduler.reschedule_job('daily_report_job', trigger='cron', hour=int(hh), minute=int(mm))
    await m.answer(f"✅ Время отчета: {hh}:{mm} (МСК)")

@dp.message(F.text.contains("Список юзеров"))
async def list_users(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    res = subprocess.run(f"docker exec {CONTAINER_NAME} sh -c 'ls *.conf'", shell=True, capture_output=True, text=True)
    users = [u.replace('.conf', '') for u in res.stdout.strip().split('\n') if u]
    await m.answer("**Юзеры:**\n" + "\n".join([f"👤 `{u}`" for u in users]) if users else "Пусто.", parse_mode="Markdown")

@dp.message(F.text.contains("Создать юзера"))
async def ask_add(m: types.Message, state: FSMContext):
    if m.from_user.id == ADMIN_ID:
        await m.answer("Имя (лат):")
        await state.set_state(Form.waiting_for_add)

@dp.message(Form.waiting_for_add)
async def proc_add(m: types.Message, state: FSMContext):
    name = m.text.strip()
    if not is_valid_name(name):
        await m.answer("❌ Ошибка в имени.")
        return
    await state.clear()
    subprocess.run(f'printf "2\n{name}\n" | docker exec -i {CONTAINER_NAME} awguser', shell=True)
    conf = subprocess.run(f'docker exec {CONTAINER_NAME} cat {name}.conf', shell=True, capture_output=True, text=True).stdout
    if "[Interface]" in conf:
        f_p, q_p = f"{name}.conf", f"{name}.png"
        with open(f_p, "w") as f: f.write(conf)
        segno.make(conf).save(q_p, scale=10)
        await m.answer_photo(FSInputFile(q_p), caption=f"QR: {name}")
        await m.answer_document(FSInputFile(f_p))
        os.remove(f_p); os.remove(q_p)

@dp.message(F.text.contains("Удалить юзера"))
async def ask_del(m: types.Message, state: FSMContext):
    if m.from_user.id == ADMIN_ID:
        await m.answer("Имя:")
        await state.set_state(Form.waiting_for_delete)

@dp.message(Form.waiting_for_delete)
async def proc_del(m: types.Message, state: FSMContext):
    name = m.text.strip()
    await state.clear()
    subprocess.run(f'printf "3\n{name}\n" | docker exec -i {CONTAINER_NAME} awguser', shell=True)
    subprocess.run(f'docker exec {CONTAINER_NAME} rm {name}.conf', shell=True)
    await m.answer(f"✅ {name} удален")

@dp.message(F.text.contains("Обновить конфиги"))
async def up_conf(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        rep = await get_traffic_report()
        await m.answer(f"📊 Отчет перед сбросом:\n{rep}", parse_mode="Markdown")
        subprocess.run(f"docker exec {CONTAINER_NAME} awgstart", shell=True)
        await m.answer("✅ Конфиги обновлены, счетчики сброшены.")

async def main():
    scheduler.add_job(send_daily_report, 'cron', hour=8, minute=0, id='daily_report_job')
    scheduler.add_job(check_container_health, 'interval', minutes=10)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try: asyncio.run(main())
    except: pass