# 💌 LoveStory Telegram Bot

Інтерактивний квест-бот для коханої людини 🥰  
Створено з ❤️ спеціально для особливих моментів.

---

## 📦 Встановлення залежностей

Почни з установки необхідних Python-модулів:

```bash
pip install -r requirements.txt
````

> Якщо файл `requirements.txt` відсутній, установи вручну:

```bash
pip install openai==0.28
pip install python-telegram-bot==13.15
```

---

## ⚙️ Налаштування

1. Зкопіюй файл `config_template.py`:

```bash
cp config_template.py config.py
```

2. Відредагуй `config.py`:

* 🔑 Заміни `OPENAI_API_KEY` на свій дійсний ключ OpenAI
* 🤖 Вкажи `BOT_TOKEN` — токен Telegram-бота
* ✅ Додай список правильних відповідей у `VALID_ANSWER_RAW_LIST`
* 🌸 За бажанням налаштуй шаблони привітань або підказок

---

## 🚀 Запуск бота

### 🧪 Тестовий запуск

Запусти бота вручну:

```bash
python3 bot.py
```

### 🛠️ Автоматичний запуск як сервіс

1. Створи `systemd` юніт:

```bash
sudo nano /etc/systemd/system/lovestory-bot.service
```

2. Встав наступне:

```ini
[Unit]
Description=LoveStory Telegram Bot
After=network.target

[Service]
WorkingDirectory=/root/wedding-telegram-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

> 🔁 Заміни `/root/wedding-telegram-bot` на актуальний шлях до каталогу з ботом.

3. Активуй та запусти:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable lovestory-bot
sudo systemctl start lovestory-bot
```

4. Перевір логи:

```bash
journalctl -u lovestory-bot.service -f
```

---

## 📂 Структура проекту

```
wedding-telegram-bot/
├── bot.py               # Основна логіка бота
├── config.py            # Конфігурація (в .gitignore)
├── config_template.py   # Приклад конфігурації
├── requirements.txt     # Список залежностей
├── .gitignore
└── README.md
```

---

## 🔐 Безпека

* `config.py` внесено в `.gitignore`, щоб не потрапляв у репозиторій
* **Ніколи** не публікуй свої API-ключі в GitHub

---

## 📣 Зворотний зв'язок

Автор: [@kiborg85](https://github.com/kiborg85)
Проект створено з любов’ю ❤️
