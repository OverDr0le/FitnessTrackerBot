from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User


async def orm_save_user(session: AsyncSession, data: dict):

    result = await session.execute(
        select(User).where(User.telegram_id==data["telegram_id"])
    )
    user = result.scalar_one_or_none()

    # Новый пользователь -> сохраняем профиль
    if user is None:
        user = User(
        telegram_id = data["telegram_id"],
        height = data["set_height"],
        weight=data["set_weight"],
        sex = data["set_sex"],
        age=data["set_age"],
        city = data["set_city"],
        calories_goal = data["calories_goal"],
        water_goal = data["water_goal"]
        )
        session.add(user)
    else:
        user.height = data["set_height"]
        user.weight = data["set_weight"]
        user.sex = data["set_sex"]
        user.age = data["set_age"]
        user.city = data["set_city"]
        user.calories_goal = data["calories_goal"]
        user.water_goal = data["water_goal"]
        
    await session.commit()
    

