from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, Message, CallbackQuery

import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict
    ):
        if event.message:
            logger.info(f"Получено сообщение: {event.message.text}")
        elif event.callback_query:
            logger.info(f"Получено сообщение: {event.callback_query.data}")
            
        return await handler(event, data)