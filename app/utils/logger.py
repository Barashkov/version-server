import logging
import sys
from app.config import Config


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger
