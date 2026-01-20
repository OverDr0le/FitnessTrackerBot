import asyncio
import logging

from aiogram import Bot, Dispatcher
from configs.config_reader import config
from database.engine import create_db, drop_db, engine
from handlers import common,menu,profile,change_calories, update_calories, update_water, update_activity, progress_check
from middlewares.db import DbUserRequiered, DataBaseSession
from middlewares.logging import LoggingMiddleware
from database.engine import session_maker

from aiohttp import web

async def health(request):
    return web.Response(text="OK")

async def run_http():
    app = web.Application()
    app.router.add_get("/",health)

    web.run_app(app,host="0.0.0.0",port = config.port)

async def on_startup(bot):
    
    run_param = config.run_param
    if run_param:
        await drop_db()
    
    await create_db()

async def on_shutdown(bot):
    print("Бот лёг")
    await bot.session.close()
    await engine.dispose()



async def main():
    logging.basicConfig(
    level=logging.WARNING
    )
    logging.getLogger("middlewares.logging").setLevel(logging.INFO)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

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
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    await asyncio.gather(
        main(),
        asyncio.to_thread(run_http)
    )
