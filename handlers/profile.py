from aiogram.filters.command import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

router = Router()

class SetProfile(StatesGroup):
    set_height = State()
    set_weight = State()
    set_age = State()
    set_sex = State()
    set_city = State()

# Создаём общую точку входа в FSM для callback и Command
async def start_profile_edit(message, state: FSMContext):
    await state.clear()
    await state.set_state(SetProfile.set_height)
    await message.answer(text="Введите ваш рост в **см**:", parse_mode=ParseMode.MARKDOWN_V2)

# Вход при помощи инлайн клавиатуры
@router.callback_query(F.data == "set_profile")
async def profile_edit_by_callback(callback: CallbackQuery, state: FSMContext):
    await start_profile_edit(callback.message, state)
    await callback.answer()

@router.message(Command('set_profile'))
async def profile_edit_by_command(message: Message, state: FSMContext):
    await start_profile_edit(message=message,state = state)

    # Добавить FSM и кнопку отмены в common.py