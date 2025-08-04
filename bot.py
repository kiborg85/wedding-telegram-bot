import logging
import time
import random
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, OPENAI_API_KEY

# === Настройка логирования ===
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# === OpenAI API ===
openai.api_key = OPENAI_API_KEY

# === Хранилища состояния ===
attempts = {}
completed_users = set()

# === Фиксированные компліменти (на случай ошибки) ===
FALLBACK_COMPLIMENTS = [
    "🌸 Твоя усмішка — моє натхнення.",
    "✨ Ти робиш цей світ кращим просто своєю присутністю.",
    "💫 Кожна мить з тобою — справжній подарунок.",
    "🌷 Я найщасливіший, що ти — моя.",
    "🦋 Твої очі яскравіші за всі зірки.",
    "🌹 Ти — моя любов, моє серце, моє все.",
    "🎀 Я кохаю тебе ще більше, ніж учора.",
    "💖 Ти — найкраще, що зі мною сталося.",
]

# === Генератор компліментів через OpenAI ===
def generate_compliment():
    logger.info("Вызов: generate_compliment()")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ти романтичний асистент. Згенеруй одне коротке, щире і красиве речення-комплімент "
                        "українською мовою, як для коханої людини. "
                        "Починай речення з відповідного емодзі — квітка, серце або зоря. Лише один рядок без зайвого."
                    )
                },
                {
                    "role": "user",
                    "content": "Комплімент для неї"
                }
            ],
            temperature=0.9,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI error: {e}")
        return random.choice(FALLBACK_COMPLIMENTS)

# === Нормализация ввода ===
def normalize_input(text):
    logger.info(f"Вызов: normalize_input('{text}')")
    text = text.lower()
    lat_to_cyr = {
        'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'h': 'н',
        'i': 'і', 'k': 'к', 'm': 'м', 'o': 'о', 'p': 'р',
        't': 'т', 'x': 'х', 'y': 'у'
    }
    text = ''.join(lat_to_cyr.get(ch, ch) for ch in text)
    allowed = set("абвгдеєжзийклмнопрстуфхцчшщьюяіїґ0123456789")
    return ''.join(ch for ch in text if ch in allowed)

# === Допустимі відповіді ===
VALID_ANSWERS = {normalize_input(x) for x in [
    "853",
    "260051",
    "1-но 260051",
    "1но260051"
]}

# === Команда /start ===
def start(update: Update, context: CallbackContext):
    logger.info(f"Вызов: start() от chat_id={update.effective_chat.id}")
    chat_id = update.effective_chat.id

    context.bot.send_message(
        chat_id=chat_id,
        text="💖 Ти — найкрасивіша, найрозумніша та найчудовіша жінка у світі.\n\nІ цей квест створено лише для тебе 🌟"
    )

    time.sleep(5)

    context.bot.send_message(
        chat_id=chat_id,
        text="🧩 Перший етап:\n\nВведи число, що зберігає силу нашої обіцянки, зафіксованої в той день, коли ми стали однією родиною."
    )

# === Обробка повідомлень ===
def check_number(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_input = normalize_input(update.message.text.strip())
    logger.info(f"Вызов: check_number() від chat_id={chat_id} | Введено: {user_input}")

    if chat_id in completed_users:
        compliment = generate_compliment()
        context.bot.send_message(chat_id=chat_id, text=compliment)
        return

    if user_input in VALID_ANSWERS:
        completed_users.add(chat_id)
        context.bot.send_message(
            chat_id=chat_id,
            text="✅ Вірно! А ось і твоя наступна підказка:\n\n📍 Зазирни туди, де ми вперше сказали 'я тебе кохаю' ❤️"
        )
        return

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

# === Точка входу ===
def main():
    logger.info("Бот запускается...")
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_number))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
