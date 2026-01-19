from aiogram.filters.command import Command, CommandObject
from aiogram.filters import StateFilter
from aiogram import Router,F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from services.daily_stats import OrmUserDailyStats
from filters.profile_filter import IsNumberInRange
from keyboards.activity_kb import activity_kb

'''
=====================================================
БОЛЬШОЕ ПРИМЕЧАНИЕ: Поскольку список доступных активностей ограничен (ввиду отсутствия русскоязычного апи бесплатного)
То добавление активности логичнее реализовать при помощи клавиатуры, а не при помощи аргументов command, ибо
Пользователь вряд ли знает, что доступно ему всего-лишь 4 вида активности при вводе команды.
=====================================================
'''
# Словарь "Название активности": расход ккал\час. Значения расходов ккал брались из разных источников
activity_dict = {
    "Прогулка": 300,
    "Бег (средний темп)": 600,
    "Плавание": 400,
    "Силовая тренировка": 250
}

class ActivityState(StatesGroup):
    activity_type = State()
    duration_mnts = State()


router = Router()


@router.callback_query(F.data == "add_activity", StateFilter(None))
async def start_activity(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.clear()

    await callback.message.answer(
        "Пожалуйста, выберите тип активности 💪",
        reply_markup= activity_kb()
    )
    
    callback.answer()
    await state.set_state(ActivityState.activity_type)

@router.message(ActivityState.activity_type, F.text.in_(activity_dict.keys()))
async def process_type(message: Message, state: FSMContext):
    await state.update_data(activity_type = message.text)
    await message.answer(
        "Введите продолжительность тренировки в минутах ⏳"
    )
    await state.set_state(ActivityState.duration_mnts)

@router.message(ActivityState.activity_type)
async def incorrect_type(message: Message):
    await message.answer(
        "Мне не известна данная активность 🙁\nПожалуйста выберите из  предложенных ниже или отмените ввод при помощи /cancel",
        reply_markup= activity_kb()
    )

@router.message(ActivityState.duration_mnts, IsNumberInRange(1,400))
async def final_process(message: Message, state:FSMContext, session: AsyncSession):
    await state.update_data(duration_mnts = int(message.text))

    data = await state.get_data()
    kcal_per_hour = activity_dict[data["activity_type"]]
    duration = data["duration_mnts"]
    additional_water = 200*round(duration/30)

    try:
        user_stats = OrmUserDailyStats(session)
        today = await user_stats.get_today(message.from_user.id)
        user_weight = today.user.weight

        # Формула, которая фиктивно учитывает вес человека, взята у llm.
        burned_kcal = round(kcal_per_hour*(duration/60) * (user_weight/70)**0.75)

        stats = await user_stats.increment(
            telegram_id= message.from_user.id,
            field = "calories_burned",
            value = burned_kcal
        )

        await user_stats.increment(
            telegram_id= message.from_user.id,
            field = "water_consumed",
            value = -additional_water # Вычитаем воду, которая ушла на тренировку чтобы соблюдать баланс
        )

        await session.commit()

        await message.answer(
            f"{data['activity_type']} {duration} минут - {burned_kcal} ккал. Дополнительно: выпейте {additional_water} мл воды 💧"
        )

    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка обновления воды."
        )
    
    finally:
        await state.clear()

@router.message(ActivityState.duration_mnts)
async def incorrect_duration(message: Message):
    await message.answer(
        "Неверный ввод. Длительность активности от 1 до 400 минут ⚠️"
    )


    




