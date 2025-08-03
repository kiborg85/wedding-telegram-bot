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

def normalize_input(text):
    # Приводим к нижнему регистру
    text = text.lower()

    # Заменяем похожие латинские буквы на кириллические
    lat_to_cyr = {
        'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н',
        'i': 'і', 'k': 'к', 'm': 'м', 'o': 'о', 'p': 'р',
        't': 'т', 'x': 'х', 'y': 'у'
    }
    text = ''.join(lat_to_cyr.get(ch, ch) for ch in text)

    # Удаляем пробелы, дефисы и другие лишние символы
    allowed = set("абвгдеєжзийклмнопрстуфхцчшщьюяіїґ0123456789")
    text = ''.join(ch for ch in text if ch in allowed)

    return text

# Множество правильных ответов (уже нормализованных)
VALID_ANSWERS = {normalize_input(x) for x in [
    "853",
    "260051",
    "1-но 260051",
    "1но260051"
]}

def check_number(update: Update, context: CallbackContext):
    user_input = normalize_input(update.message.text.strip())
    if user_input in VALID_ANSWERS:
        update.message.reply_text(
            "✅ Вірно! А ось і твоя наступна підказка:\n\n📍 Зазирни туди, де ми вперше сказали 'я тебе кохаю' ❤️"
        )
    else:
        update.message.reply_text("❌ Неправильний номер. Спробуй ще раз 🕵️")


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_number))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
