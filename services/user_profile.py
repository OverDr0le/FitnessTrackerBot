from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserProfile:
    def __init__(self,session: AsyncSession):
        self.session = session
    
    # Получаем профиль пользователя
    async def get_profile(self, telegram_id:int):

        result = await self.session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )
        profile = result.scalar_one_or_none()

        return profile
    
    # Сохраняем или изменяем профиль пользователя
    async def save_profile(self, data: dict):
        user = await self.get_profile(telegram_id=data["telegram_id"])
        
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
            self.session.add(user)

        # Пользователь существует -> обновляем профиль
        else:
            user.height = data["set_height"]
            user.weight = data["set_weight"]
            user.sex = data["set_sex"]
            user.age = data["set_age"]
            user.city = data["set_city"]
            user.calories_goal = data["calories_goal"]
            user.water_goal = data["water_goal"]
        
        await self.session.commit()



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