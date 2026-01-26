import telebot
from datetime import date, time, datetime
import os
import logging
import sqlite3

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ваш токен от BotFather
TOKEN = '8058652594:AAHF2FI4zm9T9dvmR4Z2CQ-mbfVRkdHpVSs'

# ID чата, куда отправлять логи (группа/канал)
LOG_CHAT_ID = -1003601117936  # замените на свой ID


# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# 1. Полное расписание на день (0=понедельник, ..., 6=воскресенье)
WEEK_INFO = {
    0: "Понедельник:\n"
        "1. Английский язык (каб. 40) — 8:15–8:55\n"
        "2. Биология (каб. 23) — 9:00–9:40\n"
        "3. Физика (каб. 31) — 9:50–10:30\n"
        "4. РОВ (каб. 38) — 10:45–11:25\n"
        "5. Литература (каб. 31) — 11:40–12:20\n"
        "6. Алгебра (каб. 35) — 12:35–13:15\n"
        "7. Физическая культура — 13:25–14:05\n"
        "8. Английский язык (каб. 25) — 14:15–14:55",

    1: "Вторник:\n"
        "1. История (каб. 38) — 8:15–8:55\n"
        "2. Химия (каб. 41) — 9:00–9:40\n"
        "3. Геометрия (каб. 35) — 9:50–10:30\n"
        "4. Литература (каб. 27) — 10:45–11:25\n"
        "5. Английский язык (каб. 40/25) — 11:40–12:20\n"
        "6. Вероятность и статистика (каб. 35) — 12:35–13:15\n"
        "7. География (каб. 39) — 13:25–14:05\n"
        "8. ОБЗР (каб. 39) — 14:15–14:55",

    2: "Среда:\n"
        "1. Нет занятий — 8:15–8:55\n"
        "2. Обществознание (музей) — 9:00–9:40\n"
        "3. Физика (каб. 31) — 9:50–10:30\n"
        "4. Химия (каб. 41) — 10:45–11:25\n"
        "5. Информатика/Английский язык (каб. 22/40) — 11:40–12:20\n"
        "6. Физическая культура — 12:35–13:15\n"
        "7. Труд (технология, каб. 2) — 13:25–14:05\n"
        "8. История (музей) — 14:15–14:55",

    3: "Четверг:\n"
        "1. Физика (каб. 31) — 8:15–8:55\n"
        "2. Биология (каб. 23) — 9:00–9:40\n"
        "3. Информатика/Английский язык (каб. 22/25) — 9:50–10:30\n"
        "4. Русский язык (каб. 24) — 10:45–11:25\n"
        "5. Алгебра (каб. 35) — 11:40–12:20\n"
        "6. «Россия — мои горизонты» — 12:35–13:15",

    4: "Пятница:\n"
        "1. География (каб. 39) — 8:15–8:55\n"
        "2. Алгебра (каб. 35) — 9:00–9:40\n"
        "3. Русский язык (каб. 2) — 9:50–10:30\n"
        "4. Геометрия (каб. 35) — 10:45–11:25\n"
        "5. Русский язык (библиотека) — 11:40–12:20\n"
        "6. Литература (библиотека) — 12:35–13:15",

    5: "Суббота: время отдыха! Займитесь хобби или встретьтесь с друзьями.",
    6: "Воскресенье: подготовка к новой неделе! Отдохните и настройтесь на понедельник."
}

# 2. Расписание по интервалам (1=понедельник, ..., 7=воскресенье)
SCHEDULE = {
    1: [  # Понедельник
        (time(8, 15), time(8, 55), "Сейчас урок английского языка (каб. 40)"),
        (time(9, 0), time(9, 40), "Сейчас перемена"),
        (time(9, 50), time(10, 30), "Сейчас урок биологии (каб. 23)"),
        (time(10, 45), time(11, 25), "Сейчас перемена"),
        (time(11, 40), time(12, 20), "Сейчас урок физики (каб. 31)"),
        (time(12, 35), time(13, 15), "Сейчас перемена"),
        (time(13, 25), time(14, 5), "Сейчас урок РОВ (каб. 38)"),
        (time(14, 15), time(14, 55), "Сейчас перемена")
    ],
    2: [  # Вторник
        (time(8, 15), time(8, 55), "Сейчас урок истории (каб. 38)"),
        (time(9, 0), time(9, 40), "Сейчас перемена"),
        (time(9, 50), time(10, 30), "Сейчас урок химии (каб. 41)"),
        (time(10, 45), time(11, 25), "Сейчас перемена"),
        (time(11, 40), time(12, 20), "Сейчас урок геометрии (каб. 35)"),
        (time(12, 35), time(13, 15), "Сейчас перемена"),
        (time(13, 25), time(14, 5), "Сейчас урок литературы (каб. 27)"),
        (time(14, 15), time(14, 55), "Сейчас перемена")
    ],
    3: [  # Среда
        (time(8, 15), time(8, 55), "Сейчас нет занятий"),
        (time(9, 0), time(9, 40), "Сейчас перемена"),
        (time(9, 50), time(10, 30), "Сейчас урок обществознания (музей)"),
       (time(10, 45), time(11, 25), "Сейчас перемена"),
        (time(11, 40), time(12, 20), "Сейчас урок физики (каб. 31)"),
        (time(12, 35), time(13, 15), "Сейчас перемена"),
        (time(13, 25), time(14, 5), "Сейчас урок химии (каб. 41)"),
        (time(14, 15), time(14, 55), "Сейчас перемена")
    ],
    4: [  # Четверг
        (time(8, 15), time(8, 55), "Сейчас урок физики (каб. 31)"),
        (time(9, 0), time(9, 40), "Сейчас перемена"),
        (time(9, 50), time(10, 30), "Сейчас урок биологии (каб. 23)"),
        (time(10, 45), time(11, 25), "Сейчас перемена"),
        (time(11, 40), time(12, 20), "Сейчас урок информатики/английского (каб. 22/25)"),
        (time(12, 35), time(13, 15), "Сейчас перемена"),
        (time(13, 25), time(14, 5), "Сейчас урок русского языка (каб. 24)"),
        (time(14, 15), time(14, 55), "Сейчас перемена")
    ],
    5: [  # Пятница
        (time(8, 15), time(8, 55), "Сейчас урок географии (каб. 39)"),
        (time(9, 0), time(9, 40), "Сейчас перемена"),
        (time(9, 50), time(10, 30), "Сейчас урок алгебры (каб. 35)"),
        (time(10, 45), time(11, 25), "Сейчас перемена"),
        (time(11, 40), time(12, 20), "Сейчас урок русского языка (каб. 2)"),
        (time(12, 35), time(13, 15), "Сейчас перемена"),
        (time(13, 25), time(14, 5), "Сейчас урок геометрии (каб. 35)"),
        (time(14, 15), time(14, 55), "Сейчас перемена")
    ],
    6: [],  # Суббота — нет уроков
    7: []   # Воскресенье — выходной
}

def get_weekday() -> int:
    """Возвращает номер дня недели: 0=понедельник, 6=воскресенье."""
    return date.today().weekday()


def get_isoweekday() -> int:
    """Возвращает номер дня недели: 1=понедельник, 7=воскресенье."""
    return date.today().isoweekday()


# Создание БД для хранения ID групп
conn = sqlite3.connect('bot_groups.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

def track_group(message):
    """Сохраняет ID и название группы, если бот в ней состоит"""
    chat = message.chat
    if chat.type in ['group', 'supergroup']:
        try:
            conn.execute('INSERT OR REPLACE INTO groups (chat_id, title) VALUES (?, ?)',
                         (chat.id, chat.title or chat.username))
            conn.commit()
        except Exception as e:
            logging.error(f"Ошибка при сохранении группы: {e}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    track_group(message)  # Отслеживаем группу
    bot.reply_to(message, (
        "Привет! Я бот расписания и отправки сообщений.\n"
        "Команды:\n"
        "/today — расписание на сегодня\n"
        "/что сейчас — что идёт прямо сейчас\n"
        "/понедельник … /воскресенье — расписание на конкретный день\n"
        "/msg <текст> <id_пользователя> — отправить сообщение пользователю\n"
        "/gmsg <текст> <id_группы> — отправить сообщение в группу\n"
        "/groups — показать все группы, где я состою\n"
        "/members <id_группы> — список участников группы (если я админ)"
    ))
    send_log_to_chat(message, "start", "Отправлено приветственное сообщение")

@bot.message_handler(commands=['today'])
def send_today_info(message):
    track_group(message)
    today_idx = get_weekday()
    info = WEEK_INFO[today_idx]
    bot.send_message(message.chat.id, info)
    send_log_to_chat(message, "today", info)

@bot.message_handler(commands=['что сейчас'])
def send_current_info(message):
    track_group(message)
    now = datetime.now().time()
    day_idx = get_isoweekday()  # 1–7

    if day_idx == 6:
        response = "Сегодня суббота — занятий нет."
    elif day_idx == 7:
        response = "Сегодня воскресенье — занятий нет."
    else:
        schedule = SCHEDULE.get(day_idx, [])
        response = "Нет занятий"

        for start, end, text in schedule:
            if start <= now <= end:
                response = text
                break

    bot.send_message(message.chat.id, response)
    send_log_to_chat(message, "что сейчас", response)

# Команды для конкретных дней недели
@bot.message_handler(commands=['понедельник'])
def send_monday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[0])
    send_log_to_chat(message, "понедельник", WEEK_INFO[0])


@bot.message_handler(commands=['вторник'])
def send_tuesday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[1])
    send_log_to_chat(message, "вторник", WEEK_INFO[1])

@bot.message_handler(commands=['среда'])
def send_wednesday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[2])
    send_log_to_chat(message, "среда", WEEK_INFO[2])

@bot.message_handler(commands=['четверг'])
def send_thursday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[3])
    send_log_to_chat(message, "четверг", WEEK_INFO[3])

@bot.message_handler(commands=['пятница'])
def send_friday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[4])
    send_log_to_chat(message, "пятница", WEEK_INFO[4])

@bot.message_handler(commands=['суббота'])
def send_saturday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[5])
    send_log_to_chat(message, "суббота", WEEK_INFO[5])


@bot.message_handler(commands=['воскресенье'])
def send_sunday(message):
    track_group(message)
    bot.send_message(message.chat.id, WEEK_INFO[6])
    send_log_to_chat(message, "воскресенье", WEEK_INFO[6])


# Обработка команд /msg и /gmsg
@bot.message_handler(func=lambda message: message.text.startswith('/msg') or message.text.startswith('/gmsg'))
def handle_send_message(message):
    track_group(message)
    args = message.text.split()
    command = args[0].lower()

    if len(args) < 3:
        bot.reply_to(message, "Используйте: /msg <текст> <id_пользователя> или /gmsg <текст> <id_группы>")
        send_log_to_chat(message, command, "Недостаточно аргументов")  # <-- Отступ 4 пробела
        return

    # Объединяем все слова между командой и ID в единый текст сообщения
    text_parts = args[1:-1]
    if not text_parts:
        bot.reply_to(message, "Текст сообщения не указан!")
        send_log_to_chat(message, command, "Текст не указан")  # <-- Отступ 4 пробела
        return
    text = ' '.join(text_parts)
    
    try:
        chat_id = int(args[-1])
    except ValueError:
        bot.reply_to(message, "ID должен быть числом!")
        send_log_to_chat(message, command, "Некорректный ID")  # <-- Отступ 4 пробела
        return

    try:
        bot.send_message(chat_id=chat_id, text=text)
        if command == '/msg':
            response = f"Сообщение отправлено пользователю {chat_id}"
        else:
            response = f"Сообщение отправлено в группу {chat_id}"
        bot.reply_to(message, response)
        send_log_to_chat(message, command, response)  # <-- Отступ 4 пробела
    except telebot.apihelper.ApiException as e:
        logging.error(f"Ошибка API при отправке сообщения: {e}")
        bot.reply_to(message, f"Ошибка при отправке: {e.description}")
        send_log_to_chat(message, command, f"Ошибка API: {e.description}")  # <-- Отступ 4 пробела
    except Exception as e:
        logging.error(f"Неожиданная ошибка при отправке сообщения: {e}")
        bot.reply_to(message, f"Неожиданная ошибка: {e}")
        send_log_to_chat(message, command, f"Неожиданная ошибка: {e}")  # <-- Отступ 4 пробела


@bot.message_handler(commands=['groups'])
def list_all_groups(message):
    """Показывает все группы, где состоит бот"""
    track_group(message)
    try:
        cursor = conn.execute('SELECT chat_id, title FROM groups')
        groups = cursor.fetchall()
        if groups:
            msg = "Все группы, где я состою:\n"
            for chat_id, title in groups:
                title = title or "Без названия"
                msg += f"ID: {chat_id} | Название: {title}\n"
        else:
            msg = "Я не состою ни в одной группе."
        bot.send_message(message.chat.id, msg)
        send_log_to_chat(message, "groups", msg)
    except Exception as e:
        logging.error(f"Ошибка при получении списка групп: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении списка групп.")
        send_log_to_chat(message, "groups", f"Ошибка: {e}")

@bot.message_handler(commands=['members'])
def get_group_members(message):
    """Получает список участников группы по ID (бот должен быть админом)"""
    track_group(message)
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "Используйте: /members <id_группы>")
        send_log_to_chat(message, "members", "Некорректный формат")
        return

    try:
        group_id = int(args[1])
    except ValueError:
        bot.reply_to(message, "ID группы должен быть числом!")
        send_log_to_chat(message, "members", "Некорректный ID")
        return

    try:
        members = bot.get_chat_members(group_id)
        msg = f"Участники группы {group_id}:\n"
        for member in members:
            user = member.user
            name = user.full_name
            username = f"@{user.username}" if user.username else "нет юзернейма"
            msg += f"- {name} ({username}) | ID: {user.id}\n"
        bot.send_message(message.chat.id, msg)
        send_log_to_chat(message, "members", f"Получено {len(members)} участников")
    except Exception as e:
        logging.error(f"Ошибка при получении участников: {e}")
        bot.send_message(message.chat.id, f"Не удалось получить участников: {e}")
        send_log_to_chat(message, "members", f"Ошибка: {e}")

def get_user_identifier(user):
    """Формирует читаемый идентификатор: @username или Имя Фамилия"""
    if user.username:
        return f"@{user.username}"
    elif user.last_name:
        return f"{user.first_name} {user.last_name}"
    else:
        return user.first_name

def send_log_to_chat(message, command, response_text):
    """Отправляет лог в указанный чат (LOG_CHAT_ID)"""
    user_tag = get_user_identifier(message.from_user)
    chat_info = f"Исходный чат: {message.chat.type} (ID: {message.chat.id})"
    if message.chat.title:
        chat_info += f" — «{message.chat.title}»"

    log_msg = (
        f"📊 **ЛОГ ВЫПОЛНЕНИЯ КОМАНДЫ**\n\n"
        f"🔹 Команда: `/{command}`\n"
        f"🔹 Ответ бота: `{response_text}`\n"
        f"🔹 Пользователь: {user_tag} (ID: {message.from_user.id})\n"
        f"{chat_info}\n"
        f"🔹 Дата: `{message.date}`"
    )
    try:
        bot.send_message(LOG_CHAT_ID, log_msg, parse_mode='Markdown')
    except Exception as e:
        print(f"[ОШИБКА] Не удалось отправить лог: {e}")

# Запуск бота
if __name__ == '__main__':
    logging.info("Бот запущен...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.critical(f"Критическая ошибка при работе бота: {e}")

