from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Главное меню бота
def main_menu() -> InlineKeyboardMarkup:
    """
    Клавиатура главного меню с кнопками для всех основных режимов бота.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🎲 Случайный факт', callback_data='menu:random')],
            [InlineKeyboardButton(text='🤖 Chat GPT', callback_data='menu:gpt')],
            [InlineKeyboardButton(text='🗣️ Диалог с личностью', callback_data='menu:talk')],
            [InlineKeyboardButton(text='🎯 Квиз', callback_data='menu:quiz')],
            [InlineKeyboardButton(text='🕹 Игра', callback_data='menu:game')],
            [InlineKeyboardButton(text='🌍 Переводчик', callback_data='menu:translate')]
        ]
    )
    return keyboard


# Клавиатура режима “Случайный факт”
def random_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки после генерации случайного факта:
    - Хочу еще факт
    - Закончить
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🎲 Хочу еще факт', callback_data='random:again')],
            [InlineKeyboardButton(text='⛔️ Закончить', callback_data='random:stop')],
        ]
    )


# Клавиатура режима GPT
def gpt_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка для выхода из режима ChatGPT.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Закончить', callback_data='gpt:stop')]
        ]
    )


# Клавиатура выбора личности для talk
def persons_keyboard(persons: dict) -> InlineKeyboardMarkup:
    """
    Кнопки для выбора личности (Pushkin, Musk, Jobs и др.)
    + кнопка отмены.
    """
    buttons = [
        [InlineKeyboardButton(text=f'{data["emoji"]} {data["name"]}', callback_data=f'talk:person:{key}')]
        for key, data in persons.items()
    ]
    buttons.append([InlineKeyboardButton(text='⛔️ Отмена', callback_data='talk:cancel')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура режима talk после начала диалога
def talk_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки во время диалога с личностью:
    - Сменить собеседника
    - Закончить диалог
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄 Сменить собеседника', callback_data='talk:change')],
            [InlineKeyboardButton(text='⛔️ Закончить', callback_data='talk:stop')],
        ]
    )


# Клавиатура выбора темы для квиза
def topics_keyboard(topics: dict) -> InlineKeyboardMarkup:
    """
    Кнопки с названиями всех тем для квиза + кнопка отмены.
    """
    buttons = [
        [InlineKeyboardButton(text=data['name'], callback_data=f'quiz:topic:{key}')]
        for key, data in topics.items()
    ]
    buttons.append([InlineKeyboardButton(text='⛔️ Отмена', callback_data='quiz:cancel')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура после ответа на вопрос квиза
def after_answer_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки после ответа на вопрос:
    - Следующий вопрос
    - Сменить тему
    - Закончить квиз
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶️ Следующий вопрос', callback_data='quiz:next')],
            [InlineKeyboardButton(text='🔄 Сменить тему', callback_data='quiz:change_topic')],
            [InlineKeyboardButton(text='🛑 Закончить квиз', callback_data='quiz:stop')],
        ]
    )


# Клавиатура для игры
def game_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶️ Начать игру', callback_data='game:start')],
            [InlineKeyboardButton(text='⛔️ Назад', callback_data='game:cancel')]
        ]
    )


def game_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Правда', callback_data='game:true')],
            [InlineKeyboardButton(text='❌ Ложь', callback_data='game:false')]
        ]
    )


def game_after_answer_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶️ Дальше', callback_data='game:next')],
            [InlineKeyboardButton(text='⛔️ Закончить', callback_data='game:stop')]
        ]
    )


def translate_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать перевод", callback_data="translate:start")],
        [InlineKeyboardButton(text="❌ Назад", callback_data="menu:main")]
    ])


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="translate:yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="translate:no"),
        ]
    ])


def after_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔁 Перевести ещё", callback_data="translate:again"),
            InlineKeyboardButton(text="❌ Выход", callback_data="translate:cancel"),
        ]
    ])