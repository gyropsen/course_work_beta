from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
from src.views import get_data, DATA_PATH


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame | Exception:
    try:
        date_end = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date_start = date_end - timedelta(days=91)
        date_interval = transactions[(str(date_end) >= transactions["Дата операции"]) &
                                     (transactions["Дата операции"] >= str(date_start)) &
                                     (transactions["Категория"] == category)]
        return date_interval
    except Exception as error:
        return error


print(spending_by_category(get_data(DATA_PATH), "Цветы", "2020-11-08 21:19:00"))
