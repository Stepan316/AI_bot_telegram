import logging
from html import escape
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from states.state import TalkStates
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt
from keyboards.inline import persons_keyboard, talk_keyboard, main_menu


router = Router()
logger = logging.getLogger(__name__)


# Словарь известных личностей
PERSONS = {
    'pushkin': {
        'name': 'Александр Пушкин',
        'emoji': "📖",
        'prompt': (
            'Ты - Александр Сергеевич Пушкин, известный русский писатель 19 века.'
            'Говори изысканно, с поэтическими оборотами.'
            'Иногда вставляй короткие стихотворные строки.'
            'Отвечай на русском языке'
        )
    },
    'musk': {
        'name': 'Илон Маск',
        'emoji': "🚀",
        'prompt': (
            'Ты - Илон Маск, предприниматель и визионер.'
            'Говори энергично, с энтузиазмом о технологиях и будущем.'
            'Упоминай Tesla, SpaceX, Mars, искусственный интеллект.'
            'Иногда шути. Отвечай на русском языке'
        )
    },
    'jobs': {
        'name': 'Стив Джобс',
        'emoji': "🖥",
        'prompt': (
            'Ты - Стив Джобс, сооснователь Apple.'
            'Говори вдохновляюще, о дизайне, простоте и революции.'
            'Часто говори о перфекционизме и любви к своему делу.'
            'Отвечай на русском языке'
        )
    },
}


# Команда /talk — вход в режим общения с личностью
@router.message(Command('talk'))
async def cmd_talk(message: Message, state: FSMContext):
    await state.clear()  # Сбрасываем предыдущее состояние
    await state.set_state(TalkStates.choosing_person)  # Устанавливаем состояние выбора личности

    try:
        photo = FSInputFile('images/talk.png')  # Фото приветствия
        await message.answer_photo(
            photo=photo,
            caption='<b>Диалог с известной личностью</b>\n\nВыбери с кем хочешь поговорить:',
            reply_markup=persons_keyboard(PERSONS)  # Кнопки с личностями
        )
    except Exception:
        # fallback на текст, если фото недоступно
        await message.answer(
            text='<b>Диалог с известной личностью</b>\n\nВыбери с кем хочешь поговорить:',
            reply_markup=persons_keyboard(PERSONS)
        )


# Выбор личности для диалога
@router.callback_query(TalkStates.choosing_person, F.data.startswith('talk:person:'))
async def on_person_choosen(callback: CallbackQuery, state: FSMContext):
    person_key = callback.data.split(':')[-1]

    if person_key not in PERSONS:
        await callback.answer('Неизвестная личность')
        return

    person = PERSONS[person_key]
    await state.update_data(person_key=person_key, history=[])  # Инициализация истории диалога
    await state.set_state(TalkStates.chatting)  # Переходим к состоянию общения

    await callback.answer(f'Начинаем разговор с {person["name"]}')

    await callback.message.edit_caption(
        caption=f'{person["emoji"]} <b>Вы разговариваете с {person["name"]}</b>\n\nНапишите что-нибудь - и получите ответ в его стиле',
        reply_markup=talk_keyboard()
    )


# Обработка сообщений в диалоге
@router.message(TalkStates.chatting, F.text)
async def cmd_talk_message(message: Message, state: FSMContext):
    data = await state.get_data()
    person_key = data['person_key']
    history = data.get('history', [])

    if person_key not in PERSONS:
        await message.answer('Что-то пошло не так. Начните заново /talk')
        await state.clear()
        return

    person = PERSONS[person_key]

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    history.append({'role': 'user', 'content': message.text})  # Добавляем сообщение пользователя

    response = await ask_gpt(
        user_message=message.text,
        system_prompt=person['prompt'],
        history=history[:-1]  # Передаем историю без последнего сообщения
    )

    history.append({'role': 'assistant', 'content': response})  # Сохраняем ответ GPT

    if len(history) > 16:
        history = history[-16:]  # Ограничиваем историю последних сообщений

    await state.update_data(history=history)

    await message.answer(
        f'{person["emoji"]} <b>{escape(person["name"])}</b>\n\n{escape(response)}',
        reply_markup=talk_keyboard()
    )


# Смена личности
@router.callback_query(TalkStates.chatting, F.data == 'talk:change')
async def cmd_talk_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(TalkStates.choosing_person)

    text = '<b>Диалог с известной личностью</b>\n\nВыбери с кем хочешь поговорить:'

    try:
        await callback.message.edit_caption(caption=text, reply_markup=persons_keyboard(PERSONS))
    except Exception:
        await callback.message.edit_text(text, reply_markup=persons_keyboard(PERSONS))


# Отмена выбора личности
@router.callback_query(TalkStates.choosing_person, F.data == 'talk:cancel')
async def cmd_talk_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    text = 'Выбери что тебя интересует:'

    try:
        await callback.message.edit_caption(caption=text, reply_markup=main_menu())
    except Exception:
        await callback.message.edit_text(text, reply_markup=main_menu())


# Выход из режима общения
@router.callback_query(TalkStates.chatting, F.data == 'talk:stop')
async def cmd_talk_stop(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()  # Удаляем сообщение с диалогом
    await callback.message.answer('Выбери что тебя интересует:', reply_markup=main_menu())