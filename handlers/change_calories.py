from aiogram.filters import Command, StateFilter
from aiogram import Router,F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from services.user_profile import UserProfile
from filters.profile_filter import IsNumberInRange


router = Router()

# Хэндлер на изменение цели по калориям
class CaloriesState(StatesGroup):
    calories_goal = State()

async def start_calories_edit(message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="Введите вашу дневную норму калорий"
    )
    await state.set_state(CaloriesState.calories_goal)


@router.message(Command("change_caloriesgoal"), StateFilter(None))
async def calories_edit_cmd(message: Message, state: FSMContext) -> None:
    await start_calories_edit(message=message,state=state)


@router.callback_query(F.data == "set_calories_goal", StateFilter(None))
async def calories_edit_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await start_calories_edit(callback.message,state)
    await callback.answer()


@router.message(CaloriesState.calories_goal, IsNumberInRange(500,7000))
async def process_calories(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(calories_goal = int(message.text))
    data = await state.get_data()
    try:
        user_profile = UserProfile(session)
        await user_profile.change(
            telegram_id=message.from_user.id,
            field = "calories_goal",
            value = data["calories_goal"]
        )

        await message.answer(text=f"Ваша норма калорий была изменена.\nВаша норма: {data["calories_goal"]} ккал")
        await state.clear()

    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка изменения калорий"
        )
        await state.clear()

@router.message(CaloriesState.calories_goal)
async def incorrect_calories(message: Message):
    await message.answer("Некорретные данные! Введите пожалуйста число от 500 до 7000:")