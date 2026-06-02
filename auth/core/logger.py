import sys
from loguru import logger

# Remove the default logger
logger.remove()

# Add a structured logger for stdout
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    level="INFO",
    serialize=True,
)

def get_logger():
    return logger
