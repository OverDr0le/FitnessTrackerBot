import asyncio
import logging

from aiogram import Bot, Dispatcher
from configs.config_reader import config
from database.engine import create_db, drop_db, engine
from handlers import common,menu,profile,change_calories, update_calories, update_water, update_activity
from middlewares.db import DbUserRequiered, DataBaseSession
from database.engine import session_maker

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
    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    
    profile.router.message.middleware(DataBaseSession(session_factory= session_maker))

    change_calories.router.message.middleware(DbUserRequiered(session_maker))
    change_calories.router.callback_query.middleware(DbUserRequiered(session_maker))
    change_calories.router.message.middleware(DataBaseSession(session_maker))

    update_calories.router.message.middleware(DbUserRequiered(session_maker))
    update_calories.router.callback_query.middleware(DbUserRequiered(session_maker))
    update_calories.router.message.middleware(DataBaseSession(session_maker))

    update_water.router.message.middleware(DbUserRequiered(session_maker))
    update_water.router.callback_query.middleware(DbUserRequiered(session_maker))
    update_water.router.message.middleware(DataBaseSession(session_maker))

    update_activity.router.callback_query.middleware(DbUserRequiered(session_maker))
    update_activity.router.message.middleware(DataBaseSession(session_maker))


    dp.include_routers(
        common.router,
        menu.router,
        profile.router,
        update_calories.router,
        update_water.router,
        update_activity.router,
        change_calories.router
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
