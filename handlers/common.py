from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.formatting import (
    Bold, as_marked_section,as_list
)
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext


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
        "/check_progress - Посмотреть прогресс по калориям, воде, сожжённым калориям",
        "/change_caloriesgoal - Изменить дневную норму калорий. По умолчанию рассчитывается из характеристик",
        "/cancel - Отменить действие",
        marker = "ℹ️ "
        )
    )
    await message.answer(**text.as_kwargs())

@router.message(Command("cancel"),StateFilter(None),default_state)
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text ="Нечего отменять",
        reply_markup= ReplyKeyboardRemove()
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text ="Действие отменено",
        reply_markup= ReplyKeyboardRemove()
    )





