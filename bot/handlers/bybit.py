from psycopg import AsyncConnection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging import Logger

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from bot.utils.bybit_manager import send_monitoring

router: Router = Router()

@router.message(Command('stop'))
async def stop_job(message: Message, scheduler: AsyncIOScheduler, command: CommandObject, logger: Logger) -> None:
    """ pausing job """
    try:
        args: list[str] = command.args.split()
        jid: str = f"{message.from_user.id}_{args[0]}"
        scheduler.pause_job(jid)
        await message.answer(f'Мониторинг {args[0]} остановлен')
        logger.debug(f'user stopped monitoring of {args[0]}')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in pausing job: {e}')

@router.message(Command('remove'))
async def remove_job(message: Message, scheduler: AsyncIOScheduler, command: CommandObject, logger: Logger) -> None:
    """ removing job """
    try:
        args: list[str] = command.args.split()
        jid: str = f"{message.from_user.id}_{args[0]}"
        scheduler.remove_job(jid)
        await message.answer(f'{args[0]} deleted from monitoring list')
        logger.debug(f'user removed monitoring of {args[0]}')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in removing job: {e}')

@router.message(Command("mono"))
async def add_crypto(message: Message, conn: AsyncConnection, scheduler: AsyncIOScheduler, command: CommandObject, logger: Logger) -> None:
    """ creating job """
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
            kwargs={
                'chat_id': message.from_user.id, 
                'category': args[1], 
                "crypto": args[0]
                },
            replace_existing=True)
        logger.debug('user send request to add crypto in monitoring list')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in creating job: {e}')