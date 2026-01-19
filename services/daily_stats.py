
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import UserDailyStats


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
            ).options(selectinload(UserDailyStats.user))
        )
        stats = result.scalar_one_or_none()

        if stats is None:
            stats = UserDailyStats(
                telegram_id = telegram_id,
                date = today
            )
            self.session.add(stats)
            await self.session.flush()

            await self.session.refresh(stats,["user"])
        
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

        return stats # Не делаем коммит, иначе сессия закрывается и не вывести цель по калориям и воде при обновлении