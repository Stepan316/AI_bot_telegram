import asyncio
import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt, speech_to_text, client
from states.state import TranslateStates
from keyboards.inline import translate_menu_kb, confirm_kb, after_kb, main_menu


router = Router()
logger = logging.getLogger(__name__)
os.makedirs("temp", exist_ok=True)


async def show_translate_menu(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        photo = FSInputFile('images/translate.png')  # Фото приветствия
        await message.answer_photo(
            photo=photo,
            caption=(
                '🌏 <b>Переводчик</b>\n\n'
                'Я умею переводить текст и голос.\n\n'
                'Нажми кнопку ниже, чтобы начать 👇'
            ),
            reply_markup=translate_menu_kb()  # Кнопка начать
        )
    except Exception:
        # Если фото недоступно, fallback на текст
        await message.answer('🌏 <b>Переводчик</b>\n\n'
                'Я умею переводить текст и голос.\n\n'
                'Нажми кнопку ниже, чтобы начать 👇', reply_markup=translate_menu_kb()
        )


# НАЧАЛО
@router.callback_query(F.data == "translate:start")
async def start_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(TranslateStates.choosing_lang)

    await callback.message.delete()

    await callback.message.answer(
        "🌍 На какой язык перевести?\n\n"
        "Напиши, например: английский, русский, казахский"
    )


# ВЫБОР ЯЗЫКА
async def normalize_lang_input(user_input: str) -> str:
    prompt = (
        f"Пользователь ввёл язык: '{user_input}'. "
        "Определи правильное название языка на русском языке или на том, на котором написано. "
        "Отвечай одним словом, например: английский, русский, казахский."
    )
    return await ask_gpt(prompt)

@router.message(TranslateStates.choosing_lang)
async def choose_language(message: Message, state: FSMContext):
    user_input = message.text.strip()
    lang = await normalize_lang_input(user_input)

    await state.update_data(target_lang=lang)
    await state.set_state(TranslateStates.confirm_lang)

    await message.answer(
        f"Ты хочешь переводить на: <b>{lang}</b>?\n\n"
        "Я буду сам определять язык текста/голоса.",
        reply_markup=confirm_kb()
    )


# ПОДТВЕРЖДЕНИЕ
@router.callback_query(F.data == "translate:yes")
async def confirm_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(TranslateStates.waiting_input)

    await callback.message.edit_text(
        "✍️ Отправь текст или голосовое сообщение"
    )


@router.callback_query(F.data == "translate:no")
async def reject_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(TranslateStates.choosing_lang)

    await callback.message.edit_text("Напиши язык заново")


# ПЕРЕВОД
async def translate_text(text: str, lang: str):
    prompt = (
        f"Определи язык текста и переведи его на {lang}.\n"
        "Отвечай только переводом.\n\n"
        f"{text}"
    )
    return await ask_gpt(prompt)


async def text_to_speech(text: str, output_file: str):
    response = await client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    audio_bytes = await response.aread()

    with open(output_file, "wb") as f:
        f.write(audio_bytes)


# ОБРАБОТКА ВВОДА
@router.message(TranslateStates.waiting_input)
async def handle_input(message: Message, state: FSMContext):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    data = await state.get_data()
    target_lang = data.get("target_lang")
    if not target_lang:
        await message.answer("Ошибка: язык не выбран")
        return

    if message.text:
        text = message.text

        translated = await translate_text(text, target_lang)

        await message.answer(
            f"🌍 Перевод:\n\n{translated}",
            reply_markup=after_kb()
        )

    elif message.voice:
        file = await message.bot.get_file(message.voice.file_id)
        path = f"temp/{file.file_id}.ogg"

        await message.bot.download_file(file.file_path, path)

        try:
            text = await speech_to_text(path)
        except Exception:
            os.remove(path)
            await message.answer("Ошибка распознавания")
            return

        translated = await translate_text(text, target_lang)

        output_path = f"temp/{file.file_id}.mp3"

        try:
            await text_to_speech(translated, output_path)
        except Exception:
            await message.answer(f"🌍 Перевод:\n\n{translated}")
            os.remove(path)
            return

        audio = FSInputFile(output_path)

        await message.answer_audio(audio)
        await asyncio.sleep(0.3)
        os.remove(output_path)
        await message.answer(
            f"🌍 Перевод:\n\n{translated}",
            reply_markup=after_kb()
        )

        os.remove(path)
        os.remove(output_path)

    else:
        await message.answer("Отправь текст или голос")


# ЕЩЁ РАЗ
@router.callback_query(F.data == "translate:again")
async def translate_again(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(TranslateStates.waiting_input)

    await callback.message.edit_text("✍️ Отправь новый текст или голос")


# Выход
@router.callback_query(F.data == 'translate:cancel')
async def cancel_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await show_translate_menu(callback.message, state)


@router.callback_query(F.data == 'menu:main')
async def cmd_translate_cancel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    text = 'Выбери что тебя интересует:'

    await callback.message.answer(text, reply_markup=main_menu())