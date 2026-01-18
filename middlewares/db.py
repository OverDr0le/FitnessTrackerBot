from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.models import User


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        async with self.session_factory() as session:
            try:
                data["session"] = session
                return await handler(event,data)
            finally:
                await session.close()
                
        
    
class DbUserRequiered(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Получаем user_id из апдейта
        if isinstance(event, Message):
            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            telegram_id = event.from_user.id
        else:
            return await handler(event, data)

        async with self.session_factory() as session:

            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            # Характеристики пользователя отсутствуют в бд
            if user is None:
                await self._notify_not_registered(event)
                return # Не вызываем логгирование воды,еды,сожжёных тренировок и изменения цели по калориям

            # Пользователь есть
            data["session"] = session
            data["user"] = user

            return await handler(event, data)

    async def _notify_not_registered(self, event: TelegramObject):

        text = (
            "Перед использованием трекера необходимо заполнить профиль.\n\n"
            "Используйте команду /set_profile"
        )

        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()

