import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile, CallbackQuery
from states.state import QuizStates
from keyboards.inline import topics_keyboard, after_answer_keyboard
from utils.quiz_generate import send_next_question, check_answer
from data.topics import TOPICS

router = Router()
logger = logging.getLogger(__name__)


# Команда /quiz — запуск квиза
@router.message(Command('quiz'))
async def cmd_quiz(message: Message, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)  # Устанавливаем состояние выбора темы

    try:
        photo = FSInputFile('images/quiz.png')  # Фото приветствия
        await message.answer_photo(
            photo=photo,
            caption=(
                '<b>Квиз с ChatGPT</b>\n'
                'Выбери тему - и погнали'
            ),
            reply_markup=topics_keyboard(topics=TOPICS)  # Кнопки с темами
        )
    except Exception:
        # Если фото недоступно, fallback на текст
        await message.answer('<b>Квиз с ChatGPT</b>\nВыбери тему - и погнали')


# Выбор темы квиза
@router.callback_query(QuizStates.choosing_topic, F.data.startswith('quiz:topic:'))
async def on_topic_choosen(callback: CallbackQuery, state: FSMContext):
    topic_key = callback.data.split(':')[-1]

    if topic_key not in TOPICS:
        await callback.answer('Неизвестная тема')
        return

    topic = TOPICS[topic_key]

    # Инициализируем состояние квиза
    await state.update_data(
        topic_key = topic_key,
        topic = topic,
        score = 0,
        total = 0,
        current_question = ''
    )
    await state.set_state(QuizStates.answering)  # Переходим к состоянию ответов
    await callback.answer(f'Тема {topic["name"]}')  # Уведомление о выборе темы

    await callback.message.edit_caption(
        caption=f'{topic["name"]} - Отличный выбор! Генерирую вопрос'
    )

    await send_next_question(callback.message, state, topic_key)  # Отправка первого вопроса


# Обработка ответа пользователя
@router.message(QuizStates.answering, F.text)
async def cmd_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data.get('current_question', '')
    score = data.get('score', 0)
    total = data.get('total', 0)

    if not current_question:
        await message.answer('Что-то пошло не так. Начни заново /quiz')
        await state.clear()
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Проверка ответа
    is_correct, explanation = await check_answer(current_question, message.text)

    if is_correct:
        result_header = '✅ <b>Верно</b>'
        await state.update_data(score=score+1, total=total+1, current_question='')
    else:
        result_header = '⛔️ <b>Неверно</b>'
        await state.update_data(score=score, total=total+1, current_question='')

    await message.answer(
        f'{result_header}\n\n'
        f"{explanation}\n\n"
        f'Счет <b>{score}/{total}</b>',
        reply_markup=after_answer_keyboard()  # Кнопки “следующий вопрос”, “сменить тему”, “выйти”
    )


# Следующий вопрос
@router.callback_query(F.data == 'quiz:next')
async def on_quiz_next(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)  # Убираем старые кнопки
    data = await state.get_data()
    topic_key = data.get('topic_key')
    await send_next_question(callback.message, state=state, topic_key=topic_key)


# Смена темы
@router.callback_query(F.data == 'quiz:change_topic')
async def on_quiz_change_topic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(score=0, total=0, current_question = '')
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        'Выбери новую тему',
        reply_markup=topics_keyboard(TOPICS)
    )


# Окончание квиза
@router.callback_query(F.data == 'quiz:stop')
async def on_quiz_stop(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = data.get('total', 0)

    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    # Вердикт по результатам
    if total == 0:
        verdict = 'Ты не ответил ни на один вопрос'
    elif score == total:
        verdict = 'Идеальный результат'
    elif score / total >= 0.75:
        verdict = 'Отличный результат'
    elif score / total >= 0.4:
        verdict = 'Неплохо, есть куда расти!'
    else:
        verdict = 'Стоит подтянуть знания'

    await callback.message.answer(
        '<b>Квиз завершен!</b>\n\n'
        f'Итого: <b>{score} из {total}</b>\n\n'
        f'{verdict}'
    )
    await callback.message.answer(
        'Чтобы выбрать тему нажми - 📚 /quiz\n\nДля выхода - ⭐ /start'
    )


# Отмена квиза
@router.callback_query(F.data == 'quiz:cancel')
async def on_quiz_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    try:
        await callback.message.edit_caption(caption='Квиз отменен\n\nЧтобы выбрать тему нажми'
                                                    ' - 📚 /quiz\n\nДля выхода - ⭐ /start')
    except Exception:
        await callback.message.edit_text('Квиз отменен\n\nЧтобы выбрать тему нажми'
                                         ' - 📚 /quiz\n\nДля выхода - ⭐ /start')