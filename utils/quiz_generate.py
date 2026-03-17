from html import escape
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from data.topics import TOPICS


# Генерация нового вопроса по теме
async def generate_answer(topic_key: str, TOPICS: dict) -> str:
    """
    Создает вопрос квиза для выбранной темы с помощью GPT.
    topic_key: ключ темы из словаря TOPICS
    TOPICS: словарь всех тем квиза
    """
    topic = TOPICS[topic_key]

    prompt = (
        f"Ты ведущий квиза.\n"
        f"Задай один интересный вопрос по теме: {topic['prompt_name']}.\n"
        "Вопрос должен иметь один четкий ответ.\n"
        "Пиши только вопрос.\n"
        "Без вступления.\n"
        "Без пояснений.\n"
        "Без ответа.\n"
        "Вопросы не должны повторяться."
    )

    return await ask_gpt(user_message=prompt)


# Проверка ответа пользователя
async def check_answer(question: str, user_answer: str) -> tuple[bool, str]:
    """
    Сравнивает ответ пользователя с правильным ответом через GPT.
    question: текст вопроса
    user_answer: ответ пользователя
    кортеж (правильность ответа, объяснение)
    """
    prompt = (
        f'Вопрос квиза: {question}\n'
        f'Ответ пользователя: {user_answer}\n\n'
        'Оцени правильность ответа. Отвечай строго в таком формате.\n'
        'Первая строка: только слово ВЕРНО или только слово НЕВЕРНО.\n'
        'Вторая строка и далее: краткое объяснение (1-2 предложения),'
        'И если ответ неверный - укажи правильный ответ.'
    )

    response = await ask_gpt(user_message=prompt)

    # Разделяем ответ GPT на строки
    lines = response.strip().split('\n')
    first_line = lines[0].strip().upper()

    is_correct = first_line.startswith('ВЕРНО')  # определяем правильность

    explanation = '\n'.join(lines[1:]).strip()

    if not explanation:
        explanation = 'Засчитано' if is_correct else 'Неправильно'

    return is_correct, explanation


# Отправка следующего вопроса пользователю
async def send_next_question(message: Message, state: FSMContext, topic_key: str):
    """
    Отправляет следующий вопрос из выбранной темы пользователю.
    message: объект сообщения от пользователя
    state: FSMContext для сохранения состояния
    topic_key: ключ выбранной темы
    """
    # Имитация печати
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    # Генерация вопроса
    question = await generate_answer(topic_key=topic_key, TOPICS=TOPICS)

    # Сохраняем текущий вопрос и тему в состоянии
    data = await state.get_data()
    await state.update_data(current_question=question, topic_key=topic_key)

    score = data.get('score', 0)
    total = data.get('total', 0)
    topic_name = TOPICS[topic_key]['name']

    # Отправляем пользователю
    await message.answer(
        f'Счет <b>{score}/{total}</b> | Тема <b>{escape(topic_name)}</b>\n\n'
        f'<b>Вопрос</b>\n{escape(question)}'
    )