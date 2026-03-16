import logging
import logging.config

from pathlib import Path

class Project:

    def __init__(self) -> None:
        self.base_dir: Path = Path(__file__).parent
        self._init_paths()
        self._create_directories()
    
    def _init_paths(self) -> None:
        """ initialization directories and files paths """
        self.tmp_dir: Path = self.base_dir / "tmp"

        self.logs_dir: Path = self.tmp_dir / "logs"
    def _create_directories(self) -> None:
        """ Creating directories """
        directories: list[Path] = [self.logs_dir, self.tmp_dir]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_str_paths(self) -> dict[str, str]:
        return {
            'base': str(self.base_dir),
            'logs': str(self.logs_dir),
            'tmp': str(self.tmp_dir)
        }

""" configuration for logs """

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'bot_formatter': {
            'format': '[%(asctime)s - %(name)s - %(levelname)s] [%(user_id)s - %(username)s]: %(message)s',
            'datafmt': '%Y-%m-%d %H:%M:%S',
            'defaults': {'user_id': '---', 'username': '---'}
        },
        'default_formatter': {
            'format': '[%(asctime)s - %(name)s - %(levelname)s]: %(message)s',
            'datafmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'bot_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'bot_formatter',
            'level': 'DEBUG',
            'filename': "logs/bot.log",
            'maxBytes': 5*1024*1024,
            'backupCount': 5,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'bot': {
            'handlers': ['bot_file'],
            'level': 'DEBUG'
        }
    }
}