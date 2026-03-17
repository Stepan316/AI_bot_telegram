import logging
from html import escape
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from states.state import GptStates
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt
from keyboards.inline import gpt_keyboard, main_menu


router = Router()
logger = logging.getLogger(__name__)


# Системный промпт для GPT
GPT_SYSTEM_PROMPT = (
    'Ты умный и дружелюбный ИИ-ассистент'
    'Отвечай четко и по делу. '
    'Отвечай на том языке, на котором написан запрос'
)
# промпт передается GPT для корректной генерации ответа


# Команда /gpt — вход в режим ChatGPT
@router.message(Command('gpt'))
async def cmd_gpt(message: Message, state: FSMContext):
    await state.set_state(GptStates.chatting)  # Устанавливаем состояние “чат с GPT”
    await state.update_data(history = [])  # Инициализируем историю сообщений

    try:
        photo = FSInputFile('images/gpt.png')  # Загружаем фото для приветствия
        await message.answer_photo(
            photo=photo,
            caption=(
                '<b>Режим ChatGPT</b>\n\n'
                'Напиши любой вопрос - я отвечу\n'
                'Контекст диалога сохраняется\n'
                'Нажми <b>Закончить</b> чтобы выйти'
            ),
            reply_markup=gpt_keyboard()  # Кнопки управления режимом GPT
        )
    except Exception as e:
        # Если фото не найдено или ошибка загрузки — отправляем текст без фото
        await message.answer(
            '<b>Режим ChatGPT</b>\n\n'
            'Напиши любой вопрос - я отвечу\n'
            'Контекст диалога сохраняется\n'
            'Нажми <b>Закончить</b> чтобы выйти'
        )


# Обработка сообщений в режиме GPT
@router.message(GptStates.chatting, F.text)
async def cmd_gpt_message(message: Message, state: FSMContext):
    data = await state.get_data()  # Получаем текущее состояние
    history = data.get('history', [])  # История сообщений

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING  # Показываем “печатает…” в Telegram
    )

    # Добавляем вопрос пользователя в историю
    history.append({'role': 'user', 'content': message.text})

    # Получаем ответ GPT
    response = await ask_gpt(
        user_message=message.text,
        system_prompt=GPT_SYSTEM_PROMPT,
        history=history[:-1]  # Передаем историю без последнего сообщения
    )

    # Добавляем ответ GPT в историю
    history.append({'role': 'assistant', 'content': response})

    # Ограничиваем историю последних 20 сообщений
    if len(history) > 20:
        history = history[-20:]

    await state.update_data(history=history)  # Обновляем данные состояния
    await message.answer(escape(response), reply_markup=gpt_keyboard())
    # escape нужен, чтобы HTML-теги в ответе GPT не ломали разметку


# Кнопка "Закончить" — выход из режима GPT
@router.callback_query(F.data == 'gpt:stop')
async def on_gpt_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Сбрасываем состояние пользователя
    await callback.answer('Выхожу из режима ChatGPT')  # Подтверждаем нажатие кнопки

    try:
        # Пытаемся изменить подпись под фото
        await callback.message.edit_caption(caption='Режим GPT завершен')
        await callback.message.answer('Выбери что тебя интересует:\n', reply_markup=main_menu())
    except Exception as e:
        # Если нет фото или нельзя редактировать подпись — редактируем текст
        await callback.message.edit_text(text='Режим GPT завершен')
        await callback.message.answer('Выбери что тебя интересует:\n', reply_markup=main_menu())