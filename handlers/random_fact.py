import logging
from html import escape
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt
from keyboards.inline import random_keyboard, main_menu


router = Router()
logger = logging.getLogger(__name__)


# Промпт для GPT: генерация случайного факта
FACT_PROMPT = (
    'Расскажи один интересный и малоизвестный факт из любой области знаний.'
    'Факт должен быть точным и удивительным. Не длиннее 3 предложений'
    'Начни сразу с факта, без вступлений вроде "Вот факт".'
)


# Основная функция для отправки случайного факта
async def send_random_fact(message: Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING  # Показываем “печатает…”
    )

    fact = await ask_gpt(user_message=FACT_PROMPT)  # Получаем факт от GPT
    safe_fact = escape(fact)  # Защищаем от HTML-тегов

    try:
        photo = FSInputFile('images/random.png')  # Фото для случайного факта
        await message.answer_photo(
            photo=photo,
            caption=f'<b>Случайный факт</b>\n\n{safe_fact}',
            reply_markup=random_keyboard()  # Кнопки “Снова”, “Закончить”
        )
    except Exception as e:
        logger.error('Не удалось отправить фото')
        await message.answer(
            f'<b>Случайный факт</b>\n\n{safe_fact}',
            reply_markup=random_keyboard()
        )  # fallback на текст без фото


# Команда /random — вывод случайного факта
@router.message(Command('random'))
async def cmd_random(message: Message):
    await send_random_fact(message)


# Callback кнопка “еще один факт” — генерируем новый факт
@router.callback_query(F.data == 'random:again')
async def cmd_random_again(callback: CallbackQuery):
    await callback.answer()  # Подтверждаем нажатие
    await callback.message.delete()  # Удаляем старый факт
    await send_random_fact(callback.message)  # Отправляем новый факт


# Callback кнопка “Закончить” — возвращаемся в главное меню
@router.callback_query(F.data == 'random:stop')
async def cmd_random_stop(callback: CallbackQuery):
    await callback.answer()  # Подтверждаем нажатие
    await callback.message.delete()  # Удаляем сообщение с фактом
    await callback.message.answer(
        'Выбери что тебя интересует:\n',
        reply_markup=main_menu()  # Главное меню
    )