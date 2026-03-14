import logging

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

def setup_logger(file_path: str,
                log_name: str = "",
                file_name: str = "app",
                file_log_level: int = logging.DEBUG,
                console_log_level: int = logging.INFO,
                maxBytes: float = 1024*1024*5,
                backupCount: int = 3) -> logging.Logger:
    """ setup logger and getting it """
    
    for lib in ['httpx', 'httpcore']:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    try:
        log_name = log_name if log_name else file_name
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        
        if logger.handlers:
            logger.handlers.clear()
        
        log_filename = f"{file_path}/{file_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_filename, 
            maxBytes=maxBytes, 
            backupCount=backupCount
        )
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s - %(name)s - %(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(logging.Formatter(
            '[%(levelname)s]: %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    except Exception as e:
        raise Exception(f"error in setting logs: {e}")