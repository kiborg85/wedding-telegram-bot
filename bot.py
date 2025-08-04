import time
import random
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, OPENAI_API_KEY

# Чат-ID пользователей, которые уже прошли этап
completed_users = set()

openai.api_key = OPENAI_API_KEY

# Список компліментів
COMPLIMENTS = [
    "🌸 Твоя усмішка — моє натхнення.",
    "✨ Ти робиш цей світ кращим просто своєю присутністю.",
    "💫 Кожна мить з тобою — справжній подарунок.",
    "🌷 Я найщасливіший, що ти — моя.",
    "🦋 Твої очі яскравіші за всі зірки.",
    "🌹 Ти — моя любов, моє серце, моє все.",
    "🎀 Я кохаю тебе ще більше, ніж учора.",
    "💖 Ти — найкраще, що зі мною сталося.",
]

def generate_compliment():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Ти ніжний романтичний асистент. Генеруй одне коротке, щире і красиве компліментне речення українською мовою, як для коханої людини."
                },
                {
                    "role": "user",
                    "content": "Зроби мені комплімент."
                }
            ],
            temperature=0.9,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "💖 Ти неймовірна — навіть ChatGPT розгубився від твоєї краси!"


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

    # Если уже прошёл — комплімент
if chat_id in completed_users:
    compliment = generate_compliment()
    context.bot.send_message(chat_id=chat_id, text=compliment)
    return


    # Правильный ответ
    if user_input in VALID_ANSWERS:
        completed_users.add(chat_id)
        context.bot.send_message(
            chat_id=chat_id,
            text="✅ Вірно! А ось і твоя наступна підказка:\n\n📍 Зазирни туди, де ми вперше сказали 'я тебе кохаю' ❤️"
        )
        return

    # Счётчик попыток
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
