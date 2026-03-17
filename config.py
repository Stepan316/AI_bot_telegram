import dotenv
import os


dotenv.load_dotenv()
# Загружаем переменные окружения из файла .env в системные переменные

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в .env")
# Получаем токен Telegram-бота из переменной окружения

TOKEN_GPT = os.getenv('TOKEN_GPT')
if not TOKEN_GPT:
    raise ValueError("Не найден TOKEN_GPT в .env")
# Получаем токен GPT из переменной окружения



