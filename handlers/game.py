import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile, CallbackQuery
from keyboards.inline import game_keyboard, game_start_keyboard, main_menu, game_after_answer_keyboard
from services.openai_service import ask_gpt
from states.state import GameStates


router = Router()
logger = logging.getLogger(__name__)


# Генерация
async def generate_statement(history: list[str]):
    prompt = (
        "Придумай одно интересное утверждение.\n"
        "Оно должно быть случайно либо правдой, либо ложью.\n"
        "То есть иногда утверждение должно быть правдой, иногда ложью.\n"
        "Не говори, правда это или ложь — только утверждение.\n"
        f"Не повторяй эти утверждения:\n{history}\n"
        "Пиши только утверждение."
    )
    return await ask_gpt(prompt)


@router.message(Command('game'))
async def show_game_menu(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        photo = FSInputFile('images/game.png')  # Фото приветствия
        await message.answer_photo(
            photo=photo,
            caption=(
                '🎮 <b>Правда или Ложь</b>\n\n'
                'Тебе будет показано утверждение.\n'
                'Попробуй угадать — правда это или ложь.'
            ),
            reply_markup=game_start_keyboard()  # Кнопка начать
        )
    except Exception:
        # Если фото недоступно, fallback на текст
        await message.answer('🎮 <b>Правда или Ложь</b>\n\n'
                'Тебе будет показано утверждение.\n'
                'Попробуй угадать — правда это или ложь.')


# Проверка
async def check_statement(statement: str):
    prompt = (
        f"Утверждение: {statement}\n"
        "Это правда или ложь?\n"
        "Ответь строго: ПРАВДА или ЛОЖЬ\n"
        "На второй строке краткое объяснение"
    )
    return await ask_gpt(prompt)


# Старт
async def start_game_logic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.answering)

    await callback.message.bot.send_chat_action(
        chat_id=callback.message.chat.id,
        action=ChatAction.TYPING
    )

    data = await state.get_data()

    history = data.get('history', [])
    score = data.get('score', 0)
    total = data.get('total', 0)

    statement = await generate_statement(history)

    # сохраняем историю
    history.append(statement)
    if len(history) > 10:
        history = history[-10:]

    await state.update_data(
        statement=statement,
        history=history,
        score=score,
        total=total
    )

    await callback.message.answer(
        f'🎮 Правда или ложь?\n'
        f'Счёт: <b>{score}/{total}</b>\n\n'
        f'{statement}',
        reply_markup=game_keyboard()
    )


# Ответ
@router.callback_query(GameStates.answering, F.data.startswith('game:'))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # УПРАВЛЕНИЕ
    if callback.data == 'game:stop':
        data = await state.get_data()
        score = data.get('score', 0)
        total = data.get('total', 0)

        await state.clear()

        await callback.message.edit_text(
            f'🎮 Игра завершена\n\n'
            f'Твой результат: <b>{score}/{total}</b>',
            reply_markup=game_start_keyboard()
        )
        return

    if callback.data == 'game:next':
        await start_game_logic(callback, state)
        return

    # ОТВЕТ
    user_choice = callback.data.split(':')[1]

    data = await state.get_data()
    statement = data.get('statement')

    if not statement:
        await state.clear()
        await callback.message.edit_text("Ошибка. Начни заново /game")
        return

    score = data.get('score', 0)
    total = data.get('total', 0)

    result = await check_statement(statement)

    lines = result.split('\n')
    correct = lines[0].strip().upper()
    explanation = '\n'.join(lines[1:]).strip()

    is_true = 'ПРАВДА' in correct  # 🔥 улучшили

    user_is_correct = (
        (user_choice == 'true' and is_true) or
        (user_choice == 'false' and not is_true)
    )

    total += 1
    if user_is_correct:
        score += 1

    await state.update_data(score=score, total=total)

    text_result = "✅ Правильно!" if user_is_correct else "❌ Неправильно!"

    await callback.message.edit_text(
        f'{statement}\n\n'
        f'{text_result}\n\n'
        f'{explanation}\n\n'
        f'Счёт: <b>{score}/{total}</b>',
        reply_markup=game_after_answer_keyboard()
    )


@router.callback_query(F.data == 'game:start')
async def start_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    await start_game_logic(callback, state)


@router.callback_query(F.data == 'game:cancel')
async def cancel_game(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Выбери что тебя интересует:',reply_markup=main_menu())