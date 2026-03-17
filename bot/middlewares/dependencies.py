import logging
import psycopg

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pybit.unified_trading import HTTP

from database.handler import check_user, get_user_data

class Logger(BaseMiddleware):
    
    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        Logger: logging.Logger = logging.getLogger('bot')
        data['logger'] = Logger
        return await handler(event, data)

class Connection(BaseMiddleware):

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        logger: logging.Logger = logging.getLogger('bot')
        logger.debug('connection with database')

        data['conn'] = self.conn
        return await handler(event, data)

class Scheduler(BaseMiddleware):

    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        self.scheduler = scheduler
    
    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        data['scheduler'] = self.scheduler

        logger: logging.Logger = logging.getLogger('bot')
        logger.debug("got scheduler")

        return await handler(event, data)
