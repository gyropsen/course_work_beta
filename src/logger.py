import logging
from pathlib import Path
from typing import Any


def setup_logging() -> Any:
    """
    Функция логгирования
    :return: Логгер
    """
    logger = logging.getLogger()
    file_handler = logging.FileHandler(str(Path(Path(__file__).parent.parent, "data", "logs.log")), "w")
    file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger
