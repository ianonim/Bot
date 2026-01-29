import telebot
from datetime import date, time, datetime
import os
import logging
import sqlite3
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Ваш токен от BotFather - ПРОВЕРЬТЕ ЕГО ПРАВИЛЬНОСТЬ!
TOKEN = '8058652594:AAEe1D7VYaOxxjlfM56JQ69vXIFFmW51P2c'

# ID чата, куда отправлять логи (группа/канал)
LOG_CHAT_ID = -1003601117936  # замените на свой ID


# БЕЛЫЙ СПИСОК пользователей (разрешённые ID)
WHITELIST = [
    7614638047,   # Пример ID пользователя
    987654321,   # Добавьте сюда ID тех, кому разрешён доступ
    # ...
]

def check_token_validity(token):
    """Проверяет валидность токена"""
    if not token or token.strip() == '':
        return False, "Токен пустой"
    
    if len(token) < 30:
        return False, "Неверный формат токена"
    
    return True, "Токен имеет правильный формат"

# Проверяем токен перед запуском
is_valid, message = check_token_validity(TOKEN)
if not is_valid:
    logging.error(f"Ошибка валидации токена: {message}")
    print(f"❌ ОШИБКА: {message}")
    print("Пожалуйста, получите новый токен у @BotFather и обновите его в коде.")
    sys.exit(1)

logging.info("Токен прошел базовую проверку формата")


try:
    # Инициализация бота
    bot = telebot.TeleBot(TOKEN)
    
    # Пробуем получить информацию о боте для проверки токена
    bot_info = bot.get_me()
    logging.info(f"✅ Бот успешно подключен: @{bot_info.username} (ID: {bot_info.id})")
    print(f"✅ Бот успешно подключен: @{bot_info.username}")
    
except Exception as e:
    logging.error(f"❌ Ошибка при подключении бота: {e}")
    print(f"❌ Ошибка при подключении бота: {e}")
    print("\nВозможные причины:")
    print("1. Токен неверный или устарел")
    print("2. Нет подключения к интернету")
    print("3. Проблемы с API Telegram")
    print("\nПолучите новый токен у @BotFather:")
    print("1. Откройте Telegram")
    print("2. Найдите @BotFather")
    print("3. Отправьте /newbot")
    print("4. Следуйте инструкциям")
    print("5. Скопируйте новый токен и замените его в коде")
    sys.exit(1)

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
        (time(9, 0), time(9, 40), "Сейчас урок биологии (каб. 23)"),
        (time(9, 50), time(10, 30), "Сейчас урок физики (каб. 31)"),
        (time(10, 45), time(11, 25), "Сейчас урок РОВ (каб. 38)"),
        (time(11, 40), time(12, 20), "Сейчас урок литературы (каб. 31)"),
        (time(12, 35), time(13, 15), "Сейчас урок алгебры (каб. 35)"),
        (time(13, 25), time(14, 5), "Сейчас урок физической культуры"),
        (time(14, 15), time(14, 55), "Сейчас урок английского языка (каб. 25)")
    ],
    2: [  # Вторник
        (time(8, 15), time(8, 55), "Сейчас урок истории (каб. 38)"),
        (time(9, 0), time(9, 40), "Сейчас урок химии (каб. 41)"),
        (time(9, 50), time(10, 30), "Сейчас урок геометрии (каб. 35)"),
        (time(10, 45), time(11, 25), "Сейчас урок литературы (каб. 27)"),
        (time(11, 40), time(12, 20), "Сейчас урок английского языка (каб. 40/25)"),
        (time(12, 35), time(13, 15), "Сейчас урок вероятности и статистики (каб. 35)"),
        (time(13, 25), time(14, 5), "Сейчас урок географии (каб. 39)"),
        (time(14, 15), time(14, 55), "Сейчас урок ОБЗР (каб. 39)")
    ],
    3: [  # Среда
        (time(8, 15), time(8, 55), "Сейчас нет занятий"),
        (time(9, 0), time(9, 40), "Сейчас урок обществознания (музей)"),
        (time(9, 50), time(10, 30), "Сейчас урок физики (каб. 31)"),
        (time(10, 45), time(11, 25), "Сейчас урок химии (каб. 41)"),
        (time(11, 40), time(12, 20), "Сейчас урок информатики/английского (каб. 22/40)"),
        (time(12, 35), time(13, 15), "Сейчас урок физической культуры"),
        (time(13, 25), time(14, 5), "Сейчас урок труда (технология, каб. 2)"),
        (time(14, 15), time(14, 55), "Сейчас урок истории (музей)")
    ],
    4: [  # Четверг
        (time(8, 15), time(8, 55), "Сейчас урок физики (каб. 31)"),
        (time(9, 0), time(9, 40), "Сейчас урок биологии (каб. 23)"),
        (time(9, 50), time(10, 30), "Сейчас урок информатики/английского (каб. 22/25)"),
        (time(10, 45), time(11, 25), "Сейчас урок русского языка (каб. 24)"),
        (time(11, 40), time(12, 20), "Сейчас урок алгебры (каб. 35)"),
        (time(12, 35), time(13, 15), "Сейчас урок «Россия — мои горизонты»")
    ],
    5: [  # Пятница
        (time(8, 15), time(8, 55), "Сейчас урок географии (каб. 39)"),
        (time(9, 0), time(9, 40), "Сейчас урок алгебры (каб. 35)"),
        (time(9, 50), time(10, 30), "Сейчас урок русского языка (каб. 2)"),
        (time(10, 45), time(11, 25), "Сейчас урок геометрии (каб. 35)"),
        (time(11, 40), time(12, 20), "Сейчас урок русского языка (библиотека)"),
        (time(12, 35), time(13, 15), "Сейчас урок литературы (библиотека)")
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
                         (chat.id, chat.title or chat.username or "Без названия"))
            conn.commit()
        except Exception as e:
            logging.error(f"Ошибка при сохранении группы: {e}")

def is_authorized(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в белом списке."""
    return user_id in WHITELIST

@bot.message_handler(commands=['helper'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
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
            "/members <id_группы> — список участников группы (если я админ)\n"
            "/status — статус бота"
        ))
        send_log_to_chat(message, "start", "Отправлено приветственное сообщение")
    except Exception as e:
        logging.error(f"Ошибка в команде /start: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке команды")


@bot.message_handler(commands=['status'])
def send_status(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        status_msg = f"✅ Бот работает\n"
        status_msg += f"👤 Имя: @{bot.get_me().username}\n"
        status_msg += f"🆔 ID: {bot.get_me().id}\n"  # <-- Одинаковый отступ с предыдущими строками
        status_msg += f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bot.reply_to(message, status_msg)
    except Exception as e:
        logging.error(f"Ошибка в команде /status: {e}")
        bot.reply_to(message, f"❌ Ошибка при получении статуса: {e}")

@bot.message_handler(commands=['today'])
def send_today_info(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        today_idx = get_weekday()
        info = WEEK_INFO.get(today_idx, "Расписание на этот день не найдено")
        bot.send_message(message.chat.id, info)
        send_log_to_chat(message, "today", info[:100])  # Отправляем первые 100 символов
    except Exception as e:
        logging.error(f"Ошибка в команде /today: {e}")
        bot.reply_to(message, "Произошла ошибка при получении расписания")

@bot.message_handler(commands=['что сейчас'])
def send_current_info(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        now = datetime.now().time()
        day_idx = get_isoweekday()  # 1–7

        if day_idx in [6, 7]:  # Суббота или воскресенье
            response = "Сегодня выходной — занятий нет."
        else:
            schedule = SCHEDULE.get(day_idx, [])
            response = "Сейчас перемена или нет занятий"

            for start, end, text in schedule:
                if start <= now <= end:
                    response = text
                    break

        bot.send_message(message.chat.id, response)
        send_log_to_chat(message, "что сейчас", response)
    except Exception as e:
        logging.error(f"Ошибка в команде 'что сейчас': {e}")
        bot.reply_to(message, "Произошла ошибка при получении текущего занятия")

# Команды для конкретных дней недели
@bot.message_handler(commands=['понедельник'])
def send_monday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[0])
        send_log_to_chat(message, "понедельник", "Расписание на понедельник")
    except Exception as e:
        logging.error(f"Ошибка в команде /понедельник: {e}")

@bot.message_handler(commands=['вторник'])
def send_tuesday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[1])
        send_log_to_chat(message, "вторник", "Расписание на вторник")
    except Exception as e:
        logging.error(f"Ошибка в команде /вторник: {e}")


@bot.message_handler(commands=['среда'])
def send_wednesday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[2])
        send_log_to_chat(message, "среда", "Расписание на среду")
    except Exception as e:
        logging.error(f"Ошибка в команде /среда: {e}")

@bot.message_handler(commands=['четверг'])
def send_thursday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[3])
        send_log_to_chat(message, "четверг", "Расписание на четверг")
    except Exception as e:
        logging.error(f"Ошибка в команде /четверг: {e}")

@bot.message_handler(commands=['пятница'])
def send_friday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[4])
        send_log_to_chat(message, "пятница", "Расписание на пятницу")
    except Exception as e:
        logging.error(f"Ошибка в команде /пятница: {e}")

@bot.message_handler(commands=['суббота'])
def send_saturday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[5])
        send_log_to_chat(message, "суббота", "Расписание на субботу")
    except Exception as e:
        logging.error(f"Ошибка в команде /суббота: {e}")

@bot.message_handler(commands=['воскресенье'])
def send_sunday(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        bot.send_message(message.chat.id, WEEK_INFO[6])
        send_log_to_chat(message, "воскресенье", "Расписание на воскресенье")
    except Exception as e:
        logging.error(f"Ошибка в команде /воскресенье: {e}")

# Обработка команд /msg и /gmsg
@bot.message_handler(func=lambda message: message.text.startswith('/msg') or message.text.startswith('/gmsg'))
def handle_send_message(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
        args = message.text.split(maxsplit=2)  # Используем maxsplit=2 чтобы не разбивать текст сообщения

        
        if len(args) < 3:
bot.reply_to(message, "Используйте: /msg <текст> <id_пользователя> или /gmsg <текст> <id_группы>")
            send_log_to_chat(message, args[0].lower(), "Недостаточно аргументов")
            return

        command = args[0].lower()
        text = args[1]
        
        try:
            chat_id = int(args[2])
        except ValueError:
            bot.reply_to(message, "ID должен быть числом!")
            send_log_to_chat(message, command, "Некорректный ID")
            return

        try:
            bot.send_message(chat_id=chat_id, text=text)
            if command == '/msg':
                response = f"Сообщение отправлено пользователю {chat_id}"
            else:
                response = f"Сообщение отправлено в группу {chat_id}"
            bot.reply_to(message, response)
            send_log_to_chat(message, command, response)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
            bot.reply_to(message, f"Ошибка при отправке: {e}")
            send_log_to_chat(message, command, f"Ошибка: {e}")
    except Exception as e:
        logging.error(f"Ошибка в обработке команды отправки сообщения: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке команды")

@bot.message_handler(commands=['groups'])
def list_all_groups(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
        track_group(message)
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
        send_log_to_chat(message, "groups", f"Найдено {len(groups)} групп")
    except Exception as e:
        logging.error(f"Ошибка при получении списка групп: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении списка групп.")
        send_log_to_chat(message, "groups", f"Ошибка: {e}")

@bot.message_handler(commands=['members'])
def get_group_members(message):
    user_id = message.from_user.id
    if not is_authorized(user_id):
        bot.reply_to(message, "❌ Доступ запрещён. Вы не в белом списке.")
        logging.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return

    try:
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
            # Получаем информацию о чате
            chat = bot.get_chat(group_id)
            if chat.type not in ['group', 'supergroup']:
                bot.reply_to(message, "Это не группа!")
                send_log_to_chat(message, "members", "Указанный ID не является группой")
                return
                
            # Получаем администраторов (бот должен быть админом)
            admins = bot.get_chat_administrators(group_id)
            
            # Проверяем, есть ли бот среди админов
            bot_is_admin = any(admin.user.id == bot.get_me().id for admin in admins)
            
            if not bot_is_admin:
                bot.reply_to(message, "Я не являюсь администратором этой группы!")
                send_log_to_chat(message, "members", "Бот не является админом группы")
                return
                
            # Получаем количество участников
            members_count = bot.get_chat_members_count(group_id)
            
            msg = f"Группа: {chat.title}\n"
            msg += f"ID: {group_id}\n"
            msg += f"Всего участников: {members_count}\n"
            msg += "\nАдминистраторы:\n"
            
            for admin in admins:
                user = admin.user
                name = user.full_name
                username = f"@{user.username}" if user.username else "нет юзернейма"
                status = "👑 Создатель" if admin.status == 'creator' else "⚡ Админ"
                msg += f"- {name} ({username}) | {status} | ID: {user.id}\n"
                
            bot.send_message(message.chat.id, msg)
            send_log_to_chat(message, "members", f"Получено {len(admins)} администраторов из группы {group_id}")
            
        except Exception as e:
            if "Forbidden" in str(e) or "Chat not found" in str(e):
                bot.reply_to(message, "Я не состою в этой группе или не имею доступа!")
            else:
                bot.reply_to(message, f"Ошибка: {e}")
            send_log_to_chat(message, "members", f"Ошибка: {e}")
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
    try:
        user_tag = get_user_identifier(message.from_user)
        chat_info = f"Исходный чат: {message.chat.type} (ID: {message.chat.id})"
        if message.chat.title:
            chat_info += f" — «{message.chat.title}»"

        # Обрезаем длинный текст для логов
        if len(response_text) > 200:
            response_preview = response_text[:200] + "..."
        else:
            response_preview = response_text

        log_msg = (
            f"📊 **ЛОГ ВЫПОЛНЕНИЯ КОМАНДЫ**\n\n"
            f"🔹 Команда: `/{command}`\n"
            f"🔹 Ответ бота: `{response_preview}`\n"
            f"🔹 Пользователь: {user_tag} (ID: {message.from_user.id})\n"
            f"🔹 Чат: {chat_info}\n"
            f"🔹 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.send_message(LOG_CHAT_ID, log_msg, parse_mode='Markdown')
    except Exception as e:
        print(f"[ОШИБКА] Не удалось отправить лог: {e}")

# Запуск бота
if __name__ == '__main__':
    logging.info("=" * 50)
    logging.info("Запуск бота расписания")
    logging.info(f"Токен: {TOKEN[:10]}...")  # Показываем только начало токена для безопасности
    logging.info("=" * 50)
    
        print("Запуск бота... Ожидание сообщений.")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        logging.error(f"Критическая ошибка при работе бота: {e}")
        print(f"❌ Бот остановлен из‑за ошибки: {e}")
