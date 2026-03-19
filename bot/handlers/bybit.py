from psycopg import AsyncConnection
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging import Logger

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from bot.utils.bybit_manager import send_monitoring
from datetime import date

router: Router = Router()
@router.message(Command('resume'))
async def resume_job(message: Message, scheduler: AsyncIOScheduler, command: CommandObject, logger: Logger) -> None:
    try:
        args: list[str] = command.args.split()
        jid: str = f"{message.from_user.id}_{args[0]}"
        scheduler.resume_job(jid)
        await message.answer(f'Мониторинг {args[0]} возобновлен')
        logger.debug(f'user resumed monitoring of {args[0]}')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in resuming job: {e}')

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
    """ adding crypto in monitoring list, monitoring type: interval"""
    try:
        args = command.args.split()
        if len(args) < 3:
            await message.answer("Недостаточно аргументов\n Формат: /mono название_крипты тип_рынка/торговли(к примеру spot) интервал_в_секундах")
        seconds = int(args[2])
        if seconds < 10:
            await message.answer(text="минимально разрешенный период 10 секунд ")
            return None

        jid = f"{message.from_user.id}_{args[0]}"
        scheduler.add_job(send_monitoring,
            trigger='interval',
            seconds=seconds,
            id=jid,
            kwargs={
                'chat_id': message.from_user.id, 
                'category': args[1], 
                "crypto": args[0]
                },
            replace_existing=True)
        logger.debug('user send request to add crypto in monitoring list')
        await message.answer('Ваша крипта была добавлена в список для мониторинга')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in creating job: {e}')

@router.message(Command('check'))
async def check_crypto(message: Message, conn: AsyncConnection, scheduler: AsyncIOScheduler, command: CommandObject, logger: Logger) -> None:
    try:
        args: list[str] = command.args.split()
        if len(args) < 3:
            await message.answer("Недостаточно аргументов\n Формат: /mono название_крипты тип_рынка/торговли(к примеру spot) время/дата(12:00 - уведомление в 12 часов, 10:12:2026 - уведомление придет 12 декабря 2026 года)")
            return None
        
        jid = f"{message.from_user.id}_{args[0]}"
        job_params: dict = {
            'id': jid,
            'replace_existing': True
        }
        data_args: list[str] = args[2].split(':')
        if len(data_args) == 2:
            job_params['trigger'] = 'cron'
            job_params['hour'] = data_args[0]
            job_params['minute'] = data_args[1]
        elif len(data_args) == 3:
            job_params['trigger'] = 'date'
            job_params['run_date'] = date(*list(map(int, data_args[::-1])))
        
        scheduler.add_job(
            send_monitoring,
            **job_params,
            kwargs = {
                'chat_id': message.from_user.id, 
                'category': args[1], 
                "crypto": args[0]
                }
        )
        logger.debug('user send request to add crypto in monitoring list, type: cron\date')
        await message.answer('Ваша крипта была добавлена в список для мониторинга')
    except Exception as e:
        await message.answer('Что-то пошло не так, проверьте входные данные')
        logger.warning(f'error in adding cron\date monitoring: {e}')