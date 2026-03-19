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
    await message.answer(text=text, parse_mode='Markdown')

@router.message(Command('list'))
async def get_jobs_list(message: Message, scheduler: AsyncIOScheduler, logger: Logger) -> None:
    """Get list of monitoring jobs"""
    logger.debug(f"User {message.from_user.id} requested jobs list")
    
    uid = str(message.from_user.id)
    jobs = scheduler.get_jobs()
    
    user_jobs = [job for job in jobs if job.id.startswith(f"{uid}_")]
    
    if not user_jobs:
        await message.answer("Нет активных задач мониторинга")
        return
    
    text = "Активный мониторинг\n\n"
    for job in user_jobs:
        crypto = job.id.split("_")[1]
        trigger = str(job.trigger).replace('date', '')
        text += f"{crypto}` — {trigger}\n"
    
    await message.answer(text)

@router.message(Command('help'))
async def help_cmd(message: Message) -> None:
    text = (
        "**Команды**\n\n"
        
        "** Профиль**\n"
        "/start — статус\n"
        "/set_bybit_keys — установить ключи\n"
        "/profile — портфель (требуются ключи)\n\n"
        
        "**Мониторинг (ключи не требуются)**\n"
        "/mono <символ> <рынок> <сек> — интервал\n"
        "   Пример: `/mono BTCUSDT spot 60`\n"
        "/check <символ> <рынок> <время/дата> — разово\n"
        "   Примеры: `/check BTCUSDT spot 15:30`\n"
        "            `/check BTCUSDT spot 19:03:2026`\n"
        "            `/check BTCUSDT spot 19:03:2026 20:20\n\n`"
        
        "**Управление (ключи не требуются)**\n"
        "/list — список задач\n"
        "/stop <символ> — пауза\n"
        "/resume <символ> — продолжить\n"
        "/remove <символ> — удалить\n"
    )
    await message.answer(text, parse_mode='Markdown')