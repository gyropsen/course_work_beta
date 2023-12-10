from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame | Exception:
    try:
        date_end = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date_start = date_end - timedelta(days=91)
        date_interval = transactions[(str(date_end) >= transactions["Дата операции"])
                                     & (transactions["Дата операции"] >= str(date_start))
                                     & (transactions["Категория"] == category)]
        logger.info("spending_by_category successfully")
        return date_interval
    except Exception as error:
        logger.error(f"spending_by_category: {error}")
        return error
