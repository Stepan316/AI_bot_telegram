🤖 AI Telegram Bot

Многофункциональный Telegram-бот с использованием AI (OpenAI), который умеет:

1. 🧠 Общаться с пользователем(в том числе в лице известной личности)
2. 🌍 Переводить текст и голос (с автоопределением языка)
3. 🎯 Проводить квизы с проверкой ответов и мини игра "правда - ложь"


🚀 Возможности:

🌍 Переводчик
1. Автоопределение языка
2. Поддержка текста и голосовых сообщений
3. Озвучка перевода
4. Подтверждение выбранного языка
5. Удобный интерфейс с кнопками


🎯 Квиз
1. Выбор темы
2. Генерация вопросов через AI
3. Проверка ответов
4. Подсчет очков
5. Кнопки:
  - Следующий вопрос
  - Сменить тему
  - Завершить


💬 AI-чат
1. Ответы на вопросы пользователя
2. Генерация текста через GPT
3. Общение с известной личностью


🛠️ Технологии

1. Python 3.13
2. aiogram (Telegram Bot API)
3. OpenAI API
4. FSM (Finite State Machine)
5. Async / Await


📁 Структура проекта

project/
| data
  |---topics.py
| handlers
  |---__init__.py
  |---commands_handler.py
  |---game.py
  |---gpt_chat.py
  |---quiz.py
  |---random_fact.py
  |---talk.py
  |---translate.py
| images
  |---game.png
  |---gpt.png
  |---quiz.png
  |---random.png
  |---talk.png
  |---translate.png
| keyboards
  |---inline.py
| services
  |---__init__.py
  |---openai_service.py
| states
  |---state.py
| utils
  |---quiz_generate.py
.gitignore
config.py
main.py
requirements.txt


⚙️ Установка

1. Клонировать репозиторий

```bash
git clone https://github.com/Stepan316/AI_bot_telegram.git
cd your-repo


🔧 Установка зависимостей:
  pip install -r requirements.txt

⚙️ Настроить переменные окружения
  Создай файл .env:
    BOT_TOKEN=your_telegram_bot_token
    OPENAI_API_KEY=your_openai_api_key


🚀 Запуск
  python main.py


👨‍💻 Автор
Степан
тг. @Stepan_520

⭐️ Поддержка
Если проект понравился — поставь ⭐️ на GitHub!
