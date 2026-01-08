import logging
from loguru import logger

def setup_logging():
    logger.add("logs/app.log", rotation="500 MB")
    return logger
