import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from configs.config_reader import config
from database.engine import create_db, drop_db, engine
from handlers import common,menu,profile,change_calories, update_calories, update_water, update_activity, progress_check
from middlewares.db import DbUserRequiered, DataBaseSession
from middlewares.logging import LoggingMiddleware
from database.engine import session_maker

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


# Настройка логгирования
logging.basicConfig(
level=logging.WARNING
)
logging.getLogger("middlewares.logging").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

#WebHook настройки
WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PATH = config.WEBHOOK_PATH
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

#Веб сервер настройки
WEBAPP_HOST = config.WEBAPP_HOST
WEBAPP_PORT = config.WEBAPP_PORT

#Настройки создания БД
RUN_PARAM = config.run_param

BOT_TOKEN = config.bot_token.get_secret_value()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")


async def on_startup(bot: Bot):
    """
    Вызывается при запуске бота
    Инициализирует БД и устанавливает webhook
    """
    logger.info("="*60)
    logger.info("Запуск WebHook бота...")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")

    #Удаляем существующий webhook
    await bot.delete_webhook(drop_pending_updates=True)

    #Устанавливаем новый webhook
    webhook_set = await bot.set_webhook(
        url = WEBHOOK_URL,
        drop_pending_updates= True
    )

    if webhook_set:
        logger.info("Webhook успешно установлен")
    else:
        logger.error("Ошибка установки webhook")
    

    if RUN_PARAM:
        logger.info("Удаление таблиц из базы данных...")
        await drop_db()

    await create_db()

async def on_shutdown(bot: Bot):
    """
    Вызывается при остановке бота
    Удаляет webhook и закрывает сессию с бд
    """
    logger.info("Остановка бота...")
    await bot.delete_webhook()
    logger.info("Webhook удалён")
    await bot.session.close()
    await engine.dispose()
    logger.info("Бот остановлен")
    logger.info("="*60)


@asynccontextmanager
async def lifespan_wrapper(bot: Bot):
    """ Обёртка для управления жизненным циклом бота"""
    await on_startup(bot)
    yield
    await on_shutdown(bot)



def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем все middlewares и роутеры
    dp.update.outer_middleware(LoggingMiddleware())
    
    for router in (
    change_calories.router,
    update_calories.router,
    update_water.router,
    update_activity.router,
    progress_check.router,  
    ):
        router.message.middleware(DbUserRequiered(session_maker))
        router.callback_query.middleware(DbUserRequiered(session_maker))

    profile.router.message.middleware(DataBaseSession(session_factory= session_maker))

    dp.include_routers(
        common.router,
        menu.router,
        profile.router,
        update_calories.router,
        update_water.router,
        update_activity.router,
        progress_check.router,
        change_calories.router
    )
    # Создаём aiohttp приложение
    app = web.Application()

    # Webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher= dp,
        bot = bot
    )

    webhook_handler.register(app, path = WEBHOOK_PATH)

    # Healthcheck endpoint
    async def healthcheck(request):
        return web.json_response({"status": "ok", "bot": "running"})
    
    app.router.add_get("/health", healthcheck)

    # Настраиваем приложение
    setup_application(app,dp, bot = bot)

    # lifespan events
    app._on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    # Запускаем веб-сервер
    logger.info("Starting web server...")
    web.run_app(
        app,
        host = WEBHOOK_HOST,
        port = WEBAPP_PORT,
    )



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка {e}",exc_info = True)
