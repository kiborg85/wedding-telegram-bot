from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, CORRECT_NUMBER  # импорт из отдельного файла

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Привет! Чтобы получить следующую подсказку, введи номер нашего свидетельства про одруження 💍"
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
