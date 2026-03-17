from psycopg import AsyncConnection
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

router: Router = Router()

@router.message(Command('stop'))
async def stop(message: Message, scheduler: AsyncIOScheduler, command: CommandObject) -> None:
    try:
        args = command.args.split()
        jid = f"{message.from_user.id}_{args[0]}"
        scheduler.pause_job(jid)
        await message.answer(f'Мониторинг {args[0]} остановлен')
    except Exception as e:
        await message.answer(f"error: {e}")

@router.message(Command("mono"))
async def add_crypto(message: Message, conn: AsyncConnection, scheduler: AsyncIOScheduler, command: CommandObject) -> None:
    try:
        args = command.args.split()
        seconds = int(args[3])
        if seconds < 10:
            await message.answer(text="минимально разрешенный период 60 секунд ")
            return None

        jid = f"{message.from_user.id}_{args[0]}"
        scheduler.add_job(send_monitoring,
            trigger=args[2],
            seconds=seconds,
            id=jid,
            args=[message.from_user.id, args[1], args[0]])
    except Exception as e:
        await message.answer(f'Error: {e}')