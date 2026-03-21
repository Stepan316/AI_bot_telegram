# 🤖 AI Telegram Bot

Многофункциональный Telegram-бот с использованием AI (OpenAI).

## 🚀 Возможности

### 🧠 AI-чат
- Ответы на вопросы пользователя
- Генерация текста через GPT
- Возможность общения в стиле известной личности

---

### 🌍 Переводчик
- Автоопределение языка
- Поддержка текста и голосовых сообщений
- Озвучка перевода (Text-to-Speech)
- Подтверждение выбранного языка
- Удобный интерфейс с кнопками

---

### 🎯 Квиз и игры
- Выбор темы
- Генерация вопросов через AI
- Проверка ответов
- Подсчет очков
- Мини-игра **"Правда или ложь"**

Кнопки управления:
- ▶️ Следующий вопрос
- 🔄 Сменить тему
- ❌ Завершить

---

## 🛠️ Технологии

- Python 3.13  
- aiogram (Telegram Bot API)  
- OpenAI API  
- FSM (Finite State Machine)  
- Async / Await  

---

## 📁 Структура проекта
project/
│
├── data/
│ └── topics.py
│
├── handlers/
│ ├── init.py
│ ├── commands_handler.py
│ ├── game.py
│ ├── gpt_chat.py
│ ├── quiz.py
│ ├── random_fact.py
│ ├── talk.py
│ └── translate.py
│
├── images/
│ ├── game.png
│ ├── gpt.png
│ ├── quiz.png
│ ├── random.png
│ ├── talk.png
│ └── translate.png
│
├── keyboards/
│ └── inline.py
│
├── services/
│ ├── init.py
│ └── openai_service.py
│
├── states/
│ └── state.py
│
├── utils/
│ └── quiz_generate.py
│
├── config.py
├── main.py
├── requirements.txt
└── .gitignore

---

## ⚙️ Установка

### 1. Клонировать репозиторий
git clone https://github.com/Stepan316/AI_bot_telegram.git
cd AI_bot_telegram

---

## ⚙️ Установка зависимости
pip install -r requirements.txt

---

## ⚙️ Настроить переменные окружения
### 1. Создай файл .env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

---

# ▶️ Запуск
python main.py

---

# ⚠️ Особенности
- Используется FSM для управления состояниями
- Поддержка текста и голосовых сообщений
- Интеграция с OpenAI API
- Асинхронная архитектура
- Обработка кнопок и callback-запросов

---

# 👨‍💻 Автор
Степан
тг. @Stepan_520

⭐️ Поддержка
Если проект понравился — поставь ⭐️ на GitHub!
