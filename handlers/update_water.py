from aiogram.filters.command import Command, CommandObject
from aiogram.filters import StateFilter
from aiogram import Router,F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from services.daily_stats import OrmUserDailyStats
from filters.profile_filter import IsNumberInRange


router = Router()

class WaterLogState(StatesGroup):
    water_ml = State()

async def add_water(message: Message, session: AsyncSession, ml: int):

    user_stats = OrmUserDailyStats(session=session)
    try:
        stats = await user_stats.increment(
            telegram_id=message.from_user.id,
            field = "water_consumed",
            value = ml
        )

        await session.commit()

        await session.refresh(stats, attribute_names=["user"])

        
        water_goal = stats.user.water_goal
        water_consumed = stats.water_consumed

        if water_consumed < water_goal:
            await message.answer(
                f"Записано: {ml} мл 💧\nОсталось выпить до нормы:{water_goal-water_consumed} мл 🎯",
            )
        else:
            await message.answer(
                f"Записано {ml} мл 💧.\nЦель по выпитой воде достигнута!🥳"
            )
    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка обновления воды."
        )


async def process_water_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Сколько мл воды вы выпили?"
    )
    await state.set_state(WaterLogState.water_ml)

# Вход по команде
@router.message(Command("log_water"))
async def cmd_logwater_msg(
    message: Message,
    command: CommandObject,
    session: AsyncSession
):
    if not command.args:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    
    try:
        ml, = command.args.split(" ", maxsplit=1)
        ml = int(ml)
        if ml <= 0 or ml >= 5000:
            await message.answer(
                "Некорректно введённое количество мл. Введите значение от 1 до 5000 мл."
            )
            return
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_water <ml>"
        )
        return
    
    await add_water(
    message=message,
    session= session,
    ml = ml
    )


    
# Вход по callback
@router.callback_query(F.data == "add_water", StateFilter(None))
async def cmd_logfood_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    await process_water_start(
        message= callback.message,
        state = state
    )
    await callback.answer()

# Ввод милилитров
@router.message(WaterLogState.water_ml,IsNumberInRange(1,5000))
async def water_ml_entered(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):  
    await add_water(
        message = message,
        session= session,
        ml = int(message.text)
    )
    
    await state.clear()


@router.message(WaterLogState.water_ml)
async def incorrect_ml(message: Message):
    await message.answer(
        "Некорректно введённое количество мл. Введите значение от 1 до 5000 мл."
    )