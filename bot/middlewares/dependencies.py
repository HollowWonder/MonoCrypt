import logging
import psycopg

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pybit.unified_trading import HTTP

from database.handler import check_user, get_user_data

class Logger():
    
    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        Logger: logging.Logger = logging.getLogger('bot')
        data['logger'] = Logger
        return await handler(event, data)

class Connection():

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        logger: logging.Logger = logging.getLogger('bot')
        logger.debug('connection with database')

        data['conn'] = self.conn
        return await handler(event, data)

class Scheduler():

    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        self.scheduler = scheduler
    
    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        data['scheduler'] = self.scheduler

        logger: logging.Logger = logging.getLogger('bot')
        logger.debug("got scheduler")

        return await handler(event, data)

class ByBit():

    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        logger: logging.Logger = logging.getLogger('bot')

        if not hasattr(event, 'from_user'):
            return await handler(event, data)
            
        uid: int = int(event.from_user.id)
        conn = data.get('conn')
        if conn is None:
            return await handler(event, data)

        if await check_user(data.get('conn'), uid) is False:
            return await handler(event, data)
        
        user_data: dict[str, str] = await get_user_data(conn, uid)
        try:
            session: HTTP = HTTP(testnet=False,
                            api_key=user_data.get('bybit_api'),
                            api_secret=user_data.get('bybit_secret_key'))
            data['bybit_session'] = session
            logger.debug(f'[user:{uid}] connection with bybit api')
        except Exception as e:
            logger.warning(f"error in creating bybit session, {uid}: {e}")
            event.answer('BYBIT API connection failed, please check your keys')
        return await handler(event, data)