import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, CORRECT_NUMBER  # импорт из отдельного файла
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Первое сообщение — романтичное
    context.bot.send_message(
        chat_id=chat_id,
        text="💖 Ты — самая красивая, умная и замечательная женщина на свете.\n\nИ это квест только для тебя 🌟"
    )

    # Подождать 5 секунд
    time.sleep(5)

    # Второе сообщение — инструкция
    context.bot.send_message(
        chat_id=chat_id,
        text="🗝️ Чтобы пройти к следующему этапу, тебе нужно ввести номер самого важного документа в нашей жизни — свидетельства про одруження 💍"
    )

def check_number(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()
    if user_input == CORRECT_NUMBER:
        update.message.reply_text("✅ Верно! А вот и твоя следующая подсказка:\n\n📍 Посмотри туда, где мы впервые сказали 'я люблю тебя' ❤️")
    else:
        update.message.reply_text("❌ Неверный номер. Попробуй ещё раз 🕵️")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_number))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
