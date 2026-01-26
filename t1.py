from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ваш токен бота (замените на реальный)
TOKEN = "ВАШ_ТОКЕН_БОТА"

async def msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /msg <текст> <id_пользователя>"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Используйте: /msg <текст> <id_пользователя>")
        return

    # Извлекаем текст и id из аргументов
    text = context.args[0]
    try:
        user_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("ID пользователя должен быть числом!")
        return

    try:
        await context.bot.send_message(chat_id=user_id, text=text)
        await update.message.reply_text(f"Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {e}")

async def gmsg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /gmsg <текст> <id_группы>"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Используйте: /gmsg <текст> <id_группы>")
        return

    # Извлекаем текст и id из аргументов
    text = context.args[0]
    try:
        group_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("ID группы должен быть числом!")
        return

    try:
        await context.bot.send_message(chat_id=group_id, text=text)
        await update.message.reply_text(f"Сообщение отправлено в группу {group_id}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {e}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("msg", msg_command))
    application.add_handler(CommandHandler("gmsg", gmsg_command))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
