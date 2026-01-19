from aiogram.filters.command import Command, CommandObject
from aiogram.filters import StateFilter
from aiogram import Router,F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from services.daily_stats import OrmUserDailyStats
from filters.profile_filter import IsNumberInRange
from utils.food import get_food_info 


router = Router()

class FoodLogState(StatesGroup):
    food_name = State()
    grams = State()
    clr_per_100g= State()

async def start_food(
        message: Message,
        state: FSMContext,
        food_name: str | None = None
):
    await state.clear()

    if food_name:
        # Сценарий, когда еда логируется при помощи команды от пользователя
        await process_food_name(message=message,state = state, food_name=food_name)
    else:
        # Сценарий от callback кнопки
        await message.answer("Введите название продукта:")
        await state.set_state(FoodLogState.food_name)


async def process_food_name(message, state: FSMContext, food_name:str) -> None:
        
    food_info = await get_food_info(food_name)

    if food_info:
        await message.answer(
            text=f"{food_info["name"]} - {food_info["calories"]} ккал на 100 г. Сколько грамм вы съели?"
        )
        await state.update_data(
            food_name=food_info["name"],
            clr_per_100g = food_info["calories"]
        )
    else:
        await message.answer("Мне не известна такая еда 😔")
        return

    await state.set_state(FoodLogState.grams)

# Вход по команде
@router.message(Command("log_food"), StateFilter(None))
async def cmd_logfood_msg(
    message: Message,
    command: CommandObject,
    state: FSMContext
):
    if not command.args:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    
    try:
        food_name, = command.args.split(" ", maxsplit=1)
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_food <food_name>"
        )
        return

    await start_food(
        message=message,
        state = state,
        food_name=food_name
    )


@router.callback_query(F.data == "add_food", StateFilter(None))
async def cmd_logfood_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    await start_food(
        message=callback.message,
        state = state,
        food_name= None
    )
    await callback.answer()

# Ввод название еды после callback
@router.message(FoodLogState.food_name)
async def food_name_entered(
    message: Message,
    state: FSMContext
):
    food_name = message.text.strip().lower()
    await process_food_name(message=message,state=state,food_name=food_name)


@router.message(FoodLogState.grams, IsNumberInRange(1,5000))
async def process_grams(message: Message, state: FSMContext, session: AsyncSession):
    grams = int(message.text)
    data = await state.get_data()

    calories = int(data["clr_per_100g"] * grams/100)
    user_stats = OrmUserDailyStats(session)

    try:
        await user_stats.increment(
            telegram_id=message.from_user.id,
            field = "calories_consumed",
            value = calories
        )
        await session.commit()
        
        await message.answer(
            f"Записано: {calories} ккал."
        )
    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка добавления калорий"
        )

    finally:
        await state.clear()

@router.message(FoodLogState.grams)
async def incorrect_grams(message: Message):
    message.answer(
        "Некорректно введённый вес продукта. Введите значение от 1 до 5000 г."
    )





