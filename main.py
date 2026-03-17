from aiogram import Bot, Dispatcher
import asyncio
import logging
from config import BOT_TOKEN
from handlers import router
from aiogram.client.default import DefaultBotProperties


async def main():  # Главная асинхронная функция запуска бота
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования: INFO (информация, предупреждения, ошибки)
        format="%(asctime)s - %(levelname)s %(message)s")  # Формат вывода логов с временем и уровнем
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='html')) # Создаем экземпляр бота с токеном и настройкой parse_mode='html' для форматирования сообщений
    dp = Dispatcher()  # Создаем диспетчер для обработки входящих обновлений
    dp.include_router(router)  # Подключаем к диспетчеру все обработчики из router
    await dp.start_polling(bot)  # Запускаем бесконечный цикл получения обновлений и их обработку


if __name__ == '__main__':  # Проверяем, что файл запускается напрямую, а не импортируется
    asyncio.run(main())  # Запускаем асинхронную функцию main() в цикле событий