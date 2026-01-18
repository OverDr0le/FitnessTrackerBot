from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User
from database.models import UserDailyStats

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
    # Пользователь существует -> обновляем профиль
    else:
        user.height = data["set_height"]
        user.weight = data["set_weight"]
        user.sex = data["set_sex"]
        user.age = data["set_age"]
        user.city = data["set_city"]
        user.calories_goal = data["calories_goal"]
        user.water_goal = data["water_goal"]
        
    await session.commit()
    

class OrmUserDailyStats:
    def __init__(self,session: AsyncSession):
        self.session = session
    
    # Получаем статистику по текущему отслеживаемому дню
    async def get_today(self, telegram_id:int):
        today = date.today()

        result = await self.session.execute(
            select(UserDailyStats).where(
                UserDailyStats.telegram_id == telegram_id,
                UserDailyStats.date == today
            )
        )
        stats = result.scalar_one_or_none()

        if stats is None:
            stats = UserDailyStats(
                telegram_id = telegram_id,
                date = today
            )
            self.session.add(stats)
            await self.session.flush()
        
        return stats
    
    # Метод для добавления воды\калорий от еды\сожжёных калорий
    async def increment(
            self,
            telegram_id: int,
            field: str,
            value: int
    ):
        stats = await self.get_today(telegram_id)

        current = getattr(stats, field)
        setattr(stats, field, current+ value)

        await self.session.commit()

        return stats
    


