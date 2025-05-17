import logging
import os
from logging import Logger
try:
    from rich.logging import RichHandler
except Exception:  # pragma: no cover - rich may not be installed
    RichHandler = logging.StreamHandler

class WorkUnitFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.wu_id = os.environ.get("WU_ID", "N/A")
        record.skill = os.environ.get("SKILL", "N/A")
        return True

def get_logger(name: str, level: str = "INFO") -> Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [WU:%(wu_id)s] [%(skill)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addFilter(WorkUnitFilter())
    logger.setLevel(level)
    return logger
