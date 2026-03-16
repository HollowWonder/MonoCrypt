import logging
import logging.config

from config import LOGGING_CONFIG, Project

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

def set_loggers(paths: dict[str, str]) -> None:
    """ setting logs"""
    LOGGING_CONFIG['handlers']['bot_file']['filename'] = f"{paths.get('logs')}/bot.log"
    logging.config.dictConfig(LOGGING_CONFIG)

def get_scheduler(DATABASE_URL: str) -> AsyncIOScheduler:
    """ creating scheduler for tasks"""
    executors = {
        'default': AsyncIOExecutor()
    }
    jobstores = {
        'default': SQLAlchemyJobStore(url=DATABASE_URL)
    }
    return AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        timezone="Europe/Moscow"
    )