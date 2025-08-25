import logging
import time
import random
from pathlib import Path
import openai
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN, OPENAI_API_KEY
from config import VALID_ANSWER_RAW_LIST


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

def generate_greeting() -> str:
    logger.info("Вызов: generate_greeting()")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ти романтичний квест-асистент. Згенеруй тепле, щире й емоційне вітання "
                        "українською мовою для коханої жінки. "
                        "Додай емоції, трохи гумору, емодзі (але не більше 4). "
                        "Привітання має бути довшим за 1 речення. Заверш — що цей квест створений лише для неї."
                    )
                },
                {
                    "role": "user",
                    "content": "Згенеруй вітання для квесту."
                }
            ],
            temperature=0.95,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI error (greeting): {e}")
        return (
            "💖 Ти — найкрасивіша, найрозумніша та найчудовіша жінка у всьому Всесвіті! "
            "Твої очі — мій космос, а усмішка — моє сонце ☀️ "
            "Цей квест — маленький подарунок, створений лише для тебе 🌸"
        )



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


#Функция для генерации ответа на неправильный ввод
def generate_wrong_answer_response(attempt_count: int = 1) -> str:
    logger.info("Вызов: generate_wrong_answer_response()")
    try:
        hint_part = (
            "Дай невелику загадкову підказку, яка натякає, що це номер зі свідоцтва про одруження."
            if attempt_count >= 2 else
            "Поки без підказки. Просто скажи, що це неправильна відповідь, але лагідно й жартівливо."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ти романтичний помічник у квесті для коханої жінки. "
                        "Коли користувач вводить неправильну відповідь, "
                        "відповідай одним рядком, ніжно, з гумором або емодзі українською мовою. "
                        f"{hint_part} Ніколи не показуй точну відповідь."
                    )
                },
                {
                    "role": "user",
                    "content": "Що сказати на неправильну відповідь?"
                }
            ],
            temperature=0.95,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI error (wrong answer): {e}")
        return random.choice([
            "❌ Ні, не так 😅 Але не здавайся!",
            "🙈 Це ще не те. Спробуй знову!",
            "🧐 Щось не сходиться... але ти близько!",
            "🤔 Цікаво... але ні. Подумай ще!"
        ])


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

VALID_ANSWERS = {normalize_input(x) for x in VALID_ANSWER_RAW_LIST}

# === Команда /start ===
def start(update: Update, context: CallbackContext):
    logger.info(f"Вызов: start() от chat_id={update.effective_chat.id}")
    chat_id = update.effective_chat.id

    completed_users.discard(chat_id)  # сбрасываем прогресс для этого пользователя
    attempts.pop(chat_id, None)       # сбрасываем счетчик попыток
    context.user_data.clear()
    context.chat_data.clear()

    greeting = generate_greeting()
    context.bot.send_message(chat_id=chat_id, text=greeting)

    time.sleep(5)

    context.bot.send_message(
        chat_id=chat_id,
        text="🧩Введи число, що зберігає силу нашої обіцянки, зафіксованої в той день, коли ми стали однією родиною."
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
            text="Вірно! А наступне відео підкаже тобі де шукати далі ;-)"
        )
        time.sleep(5)
        video_path = Path(__file__).resolve().parent.parent / "output.avi"
        with open(video_path, "rb") as video:
            context.bot.send_video(
                chat_id=chat_id,
                video=InputFile(video, filename="output.avi"),
                supports_streaming=True,
            )
        return

    attempts[chat_id] = attempts.get(chat_id, 0) + 1

    if attempts[chat_id] == 10:
        context.bot.send_message(
            chat_id=chat_id,
            text="❗ Маленька підказка:\nЦе шестизначне число з нашого свідоцтва про одруження 💍"
        )

    wrong_text = generate_wrong_answer_response(attempts[chat_id])
    context.bot.send_message(chat_id=chat_id, text=wrong_text)
    

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
