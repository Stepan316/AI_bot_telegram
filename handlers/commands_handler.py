from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.inline import main_menu

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    keyboard = main_menu()
    await message.answer('Что ты хочешь сделать?', reply_markup=keyboard)