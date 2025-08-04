import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN  # Токен хранится отдельно

# 🔐 Множество допустимих правильных відповідей
def normalize_input(text):
    text = text.lower()
    lat_to_cyr = {
        'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н',
        'i': 'і', 'k': 'к', 'm': 'м', 'o': 'о', 'p': 'р',
        't': 'т', 'x': 'х', 'y': 'у'
    }
    text = ''.join(lat_to_cyr.get(ch, ch) for ch in text)
    allowed = set("абвгдеєжзийклмнопрстуфхцчшщьюяіїґ0123456789")
    text = ''.join(ch for ch in text if ch in allowed)
    return text

VALID_ANSWERS = {normalize_input(x) for x in [
    "853",
    "260051",
    "1-но 260051",
    "1но260051"
]}

# 🔁 Счетчик попыток по chat_id
attempts = {}

# 💬 Приветствие
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    context.bot.send_message(
        chat_id=chat_id,
        text="💖 Ти — найкрасивіша, найрозумніша та найчудовіша жінка у світі.\n\nІ цей квест створено лише для тебе 🌟"
    )

    time.sleep(5)

    context.bot.send_message(
        chat_id=chat_id,
        text="🧩Введи число, що зберігає силу нашої обіцянки, зафіксованої в той день, коли ми стали однією родиною."
    )

# 🔎 Проверка ответа
def check_number(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_input = normalize_input(update.message.text.strip())

    if user_input in VALID_ANSWERS:
        attempts.pop(chat_id, None)  # сбросить счётчик
        context.bot.send_message(
            chat_id=chat_id,
            text="✅ Вірно! А ось і твоя наступна підказка:\n\n📍 Зазирни туди, де ми вперше сказали 'я тебе кохаю' ❤️"
        )
        return

    # Увеличиваем попытки
    attempts[chat_id] = attempts.get(chat_id, 0) + 1

    if attempts[chat_id] == 2:
        context.bot.send_message(
            chat_id=chat_id,
            text="❗ Маленька підказка:\nЦе шестизначне число з нашого свідоцтва про одруження 💍"
        )

    context.bot.send_message(
        chat_id=chat_id,
        text="❌ Неправильний номер. Спробуй ще раз 🕵️"
    )

# ▶️ Запуск
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_number))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
