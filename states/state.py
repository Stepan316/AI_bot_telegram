from aiogram.fsm.state import State, StatesGroup


# Состояния для режима ChatGPT
class GptStates(StatesGroup):
    chatting = State()


# Состояния для режима Talk (разговор с личностью)
class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()


# Состояния для квиза
class QuizStates(StatesGroup):
    choosing_topic = State()
    answering = State()


# Состояние для игры
class GameStates(StatesGroup):
    answering = State()


# Состояние для переводчика
class TranslateStates(StatesGroup):
    choosing_lang = State()
    confirm_lang = State()
    waiting_input = State()