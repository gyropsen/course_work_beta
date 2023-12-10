import json
import re
from pathlib import Path
from src.views import building_json_views, get_data
from src.logger import setup_logging
from src.services import get_description_operation
from src.reports import spending_by_category

logger = setup_logging()

DATA_PATH = str(Path(Path(__file__).parent.parent, "data", "operations.xls"))
VIEWS_WRITE_FILE = str(Path(Path(__file__).parent.parent, "data", "views.json"))
SERVICES_WRITE_FILE = str(Path(Path(__file__).parent.parent, "data", "services.json"))
REPORTS_WRITE_FILE = str(Path(Path(__file__).parent.parent, "data", "reports.json"))


if __name__ == '__main__':
    try:
        with open(VIEWS_WRITE_FILE, 'w') as fp:
            date = input("Введите дату в формате %Y-%m-%d %H:%M:%S: ")
            json.dump(building_json_views(date, DATA_PATH), fp,
                      ensure_ascii=False)
        logger.info("Write file views.json successfully")

        with open(SERVICES_WRITE_FILE, 'w') as fp:
            json.dump(get_description_operation(DATA_PATH, "SPAR"), fp,
                      ensure_ascii=False)
        logger.info("Write file services.json successfully")

        with open(REPORTS_WRITE_FILE, 'w') as fp:
            json.dump(spending_by_category(get_data(DATA_PATH), "Супермаркеты", date), fp,
                      ensure_ascii=False)
        logger.info("Write file reports.json successfully")
    except Exception as error:
        logger.error(error)
