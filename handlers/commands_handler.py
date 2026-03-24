from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from handlers.game import show_game_menu
from handlers.quiz import cmd_quiz
from handlers.translate import show_translate_menu
from keyboards.inline import main_menu
from handlers.random_fact import send_random_fact
from handlers.gpt_chat import cmd_gpt
from aiogram.fsm.context import FSMContext
from handlers.talk import cmd_talk
from states.state import TranslateStates


router = Router()  # Создаем локальный роутер для этих обработчиков


# Команда /start — главное меню
@router.message(Command('start'))
async def cmd_start(message: Message):
    keyboard = main_menu()  # Создаем клавиатуру главного меню
    await message.answer(
        f'Привет, <b>{message.from_user.first_name or "Гость"}</b>\n\n'
        'Я бот с ChatGPT. Выбери что тебя интересует:\n',
        reply_markup=keyboard
    )


# Команда /help — список доступных команд
@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Команды:</b>\n\n'
        '/start - Главное меню\n'
        '/random - Случайный факт\n'
        '/gpt - Диалог с ChatGPT\n'
        '/talk - Диалог с известной личностью\n'
        '/quiz - Квиз\n'
        '/game - Игра\n'
        '/translate - Переводчик\n'
        '/help - Список команд'
    )
    #Все команды здесь статические, если добавлять новые — не забудь обновить текст


# Callback кнопка "Случайный факт"
@router.callback_query(F.data == 'menu:random')
async def on_menu_random(callback: CallbackQuery):
    await callback.answer()  # Подтверждаем нажатие кнопки (убирает загрузку)
    await send_random_fact(callback.message)  # Отправляем случайный факт в чат


# Callback кнопка "ChatGPT"
@router.callback_query(F.data == 'menu:gpt')
async def on_menu_gpt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await cmd_gpt(callback.message, state)
    #state передается для хранения контекста разговора с GPT


# Callback кнопка "Диалог с известной личностью"
@router.callback_query(F.data == 'menu:talk')
async def on_menu_talk(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await cmd_talk(callback.message, state)


# Callback кнопка "Квиз"
@router.callback_query(F.data == 'menu:quiz')
async def on_menu_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await cmd_quiz(callback.message, state)


# Callback кнопка "Игра"
@router.callback_query(F.data == 'menu:game')
async def on_menu_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_game_menu(callback.message, state)


# Callback кнопка "Переводчик"
@router.callback_query(F.data == 'menu:translate')
async def on_menu_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TranslateStates.waiting_input)
    await show_translate_menu(callback.message, state)