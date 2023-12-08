import json
from typing import Hashable, Any
from pathlib import Path
import pandas as pd
import re

WRITE_FILE = str(Path(Path(__file__).parent.parent, "data", "services.json"))


def get_description_operation(path: str, pattern: re.Pattern[str]) -> list[dict[Hashable, Any]]:
    """
    Поиск описания в файле Excel
    :param path: Путь до файла с данными
    :param pattern: Искомое описание операции
    :return: json-ответ
    """
    operations = pd.read_excel(path).dropna(subset=['Номер карты']).fillna(value=0).to_dict("records")
    pattern = re.compile(pattern)
    result = [operation for operation in operations if pattern.search(operation['Описание'])]

    with open(WRITE_FILE, 'w') as fp:
        json.dump(result, fp, ensure_ascii=False)
    return result
