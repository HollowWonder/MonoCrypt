import asyncio
import aiogram
import os
import psycopg
import logging

import bot.middlewares.dependencies as mds

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from dotenv import load_dotenv

from bot.utils.bot_manager import set_bot
from bot.handlers import router
from bot.utils.dependencies import set_loggers, get_scheduler

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.handler import db_init
from config import Project

load_dotenv()

BOT_API: str = os.getenv('BOT_API')
DATABASE_URL: str = os.getenv("DATABASE_URL")
REDIS_URL: str = os.getenv("REDIS_URL")

async def main() -> None:
    project: Project = Project()
    paths: dict[str, str] = project.get_str_paths()
    set_loggers(paths)

    logger: logging.Logger = logging.getLogger('bot')
    
    scheduler: AsyncIOScheduler = get_scheduler(DATABASE_URL)
    scheduler.start()
    
    conn: psycopg.Connection = await psycopg.AsyncConnection.connect(DATABASE_URL)
    dp = None
    
    try:
        redis_client: Redis = Redis.from_url(REDIS_URL)
        storage: RedisStorage = RedisStorage(redis_client)

        await db_init(conn=conn)

        bot: Bot = Bot(token=BOT_API)
        set_bot(bot)
        dp: Dispatcher = Dispatcher(storage=storage)

        dp.update.outer_middleware(mds.Logger())
        dp.update.outer_middleware(mds.Scheduler(scheduler))
        dp.update.outer_middleware(mds.Connection(conn))

        dp.include_router(router)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await conn.close()
        if dp:
            dp.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
        