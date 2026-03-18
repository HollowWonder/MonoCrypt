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
        base_logger: logging.Logger = logging.getLogger('bot')
        
        extra = {'user_id': '---', 'username': '---'}
        if hasattr(event, "message"):
            extra = {
                'user_id': event.message.from_user.id,
                'username': event.message.from_user.username
            }

        logger = logging.LoggerAdapter(base_logger, extra=extra)

        data['logger'] = logger
        return await handler(event, data)

class Connection(BaseMiddleware):

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        data['conn'] = self.conn
        return await handler(event, data)

class Scheduler(BaseMiddleware):

    def __init__(self, scheduler: AsyncIOScheduler) -> None:
        self.scheduler = scheduler
    
    async def __call__(self, handler: Callable,
                event: TelegramObject,
                data: Any) -> Any:
        data['scheduler'] = self.scheduler
        return await handler(event, data)
