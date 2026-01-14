from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.formatting import (
    Bold, as_marked_section,as_list
)


router = Router()

@router.message(Command("start"))
async def start_menu(message: Message):
    text = "Привет! Я - твой универсальный фитнесс трекер, помогаю следить за питанием и тренировками\nСписок моих команд: /help"
    await message.answer(
        text=text,
        reply_markup= ReplyKeyboardRemove()
    )

@router.message(Command("help"))
async def cmd_help(message:Message):
    text = as_list(
        as_marked_section(
        Bold("Список доступных команд:"),
        "/start - Запуск бота",
        "/menu - Основное управление ботом",
        "/set_profile - Внести свои характеристики (рост, вес и т.д.)",
        "/log_water - Добавить выпитую воду",
        "/log_food - Добавить приём пищи",
        "/log_workout - Добавить активность",
        "/check_progress - Посмотреть прогресс по калориям, воде, сожжённым калориям",
        marker = "ℹ️ "
        )
    )
    await message.answer(**text.as_kwargs())
