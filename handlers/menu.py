from aiogram.filters.command import Command
from aiogram import Router
from aiogram.types import Message

from keyboards.menu_kb import menu_kb


router = Router()

@router.message(Command("menu"))
async def cmd_start(message: Message):
    await message.answer(
        text = "Выберите действие",
        reply_markup= menu_kb()
    )

