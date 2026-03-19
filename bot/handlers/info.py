from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from logging import Logger
from psycopg import AsyncConnection
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.utils.bybit_manager import get_bybit_profile

router: Router = Router()

@router.message(Command('profile'))
async def get_profile(message: Message, conn: AsyncConnection, logger: Logger) -> None:
    """ getting profile """
    logger.debug('request for a profile')
    uid: int = message.from_user.id
    text: str = await get_bybit_profile(conn, uid)
    await message.answer(text=text)

@router.message(Command('list'))
async def get_jobs_list(message: Message, conn: AsyncConnection, logger: Logger, scheduler: AsyncIOScheduler) -> None:
    """ getting list of jobs name for database  """
    logger.debug('user request for list of jobs')
    uid: str = str(message.from_user.id)
    text: str = (
        "---Список активов задействованных в мониторинге---\n\n"
        )
    jobs: list = scheduler.get_jobs()

    for job in jobs:
        if job.id.startswith(f"{uid}_"):
            text += str(job.id.split("_")[1]) + " | " + str(job.trigger)
    
    await message.answer(text)