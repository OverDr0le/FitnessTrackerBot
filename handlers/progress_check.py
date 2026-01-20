from aiogram import Router,F
from aiogram.types import Message
from aiogram.utils.formatting import (
    as_marked_section,as_list
)
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession
from services.daily_stats import OrmUserDailyStats


async def show_stats(message: Message,session: AsyncSession):

    try:
        daily_stats = OrmUserDailyStats(session)
        today = await daily_stats.get_today(telegram_id= message.from_user.id)


        kcal_consumed = today.calories_consumed
        kcal_burned = today.calories_burned
        kcal_goal = today.user.calories_goal

        water_consumed = today.water_consumed
        water_goal = today.user.water_goal

        if water_consumed >= water_goal:
            congrats_water = "Дневная норма воды выполнена ✅"
        else:
            congrats_water = f"Осталось {water_goal - water_consumed} мл."
        
        if kcal_consumed-kcal_burned > kcal_goal:
            kcal_msg = f"Дневная норма калорий превышена на {kcal_consumed - kcal_goal - kcal_burned} ккал."
        else:
            kcal_msg = f"Баланс: {kcal_consumed - kcal_burned} ккал."

        text = as_list(
            "📊 Прогресс:\nВода 💧:",
            as_marked_section(
                f"Выпито: {water_consumed} мл из {water_goal} мл.",
                congrats_water,
                marker = "-"
            ),
            "Калории:",
            as_marked_section(
                f"Потреблено: {kcal_consumed} ккал из {kcal_goal} ккал.",
                f"Сожжено: {kcal_burned} ккал.",
                kcal_msg,
                marker="-"
            ),
            sep = "\n\n"
        )

        await message.answer(**text.as_kwargs())
    
    except Exception as e:
        print(f"Ошибка:\n{str(e)}")
        await message.answer(
            f"Ошибка получения статистик."
        )



router = Router()


@router.message(Command("check_progress"))
async def check_cmd(message: Message, session: AsyncSession):
    await show_stats(
        message=message,
        session=session
    )
