from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import pandas as pd
import requests
import json
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

DATA_PATH = str(Path(Path(__file__).parent.parent, "data", "operations.xls"))
WRITE_FILE = str(Path(Path(__file__).parent.parent, "data", "views.json"))

result = {}


def get_greeting(date: Any) -> str:
    """
    Приветствие
    :param date: Дата
    :return: Приветствие
    """
    opts = ['Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи']
    if 4 < date.hour <= 12:
        return opts[0]
    elif 12 < date.hour <= 16:
        return opts[1]
    elif 16 < date.hour <= 24:
        return opts[2]
    else:
        return opts[3]


def get_filtered_operations(path: str) -> Any:
    """
    Чтение финансовых операций с CSV- и XLS-файлов
    :param path: Путь до файла
    :return: DataFrame всех операций
    """
    try:
        operations = pd.read_excel(path).dropna(subset=['Номер карты'])
        cards = [{"last_digits": number_card, "total_spent": 0, "cashback": 0} for number_card in
                 operations['Номер карты'].unique()]
        for card in cards:
            filtered_operations = operations.loc[
                (operations["Номер карты"] == card["last_digits"]) & (operations["Статус"] == "OK") & (
                    operations['Сумма операции'] <= 0)]
            card["total_spent"] = round(abs(filtered_operations['Сумма операции'].sum()), 2)
            card["cashback"] = round(card["total_spent"] / 100)
        return cards
    except Exception as error:
        return error


def get_top_operations(path: str) -> Any:
    """
    Топ 5 самых больших расходов
    :param path: путь чтения файла
    :return: Словари с информацией
    """
    operations = pd.read_excel(path).dropna(subset=['Номер карты'])
    filtered_operations = operations.loc[(operations["Статус"] == "OK") & (
        operations['Сумма операции'] <= 0)]
    top_max_operations = [{"date": operation["Дата операции"],
                           "amount": abs(operation["Сумма операции"]),
                           "category": operation["Категория"],
                           "description": operation["Описание"]} for operation in
                          filtered_operations.sort_values(by='Сумма операции')[:5].to_dict("records")]
    return top_max_operations


def get_stock_price(date: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Курс акции за вчерашний торговый день
    :param date: Дата
    :return: Словарь с вчерашними ценами закрытия {MSFT: 123, и т.д.}
    """
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    currencies = ["USD", "EUR"]
    stock_prices = []
    currency_rates = []
    yesterday = (date - timedelta(days=1)).strftime("%Y-%m-%d")
    for stock in stocks:
        url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&outputsize=compact'
               f'&apikey={API_KEY}')
        response = requests.get(url).json()
        print(response)
        stock_prices.append({"stock": response["Meta Data"]["2. Symbol"],
                             "price": response["Time Series (Daily)"][yesterday]["4. close"]})
    for currency in currencies:
        url = (f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={currency}'
               f'&to_symbol=RUB&apikey={API_KEY}')
        response = requests.get(url).json()
        print(response)
        currency_rates.append({"currency": response["Meta Data"]["2. Symbol"],
                               "rate": response["Time Series FX (Daily)"][yesterday]["4. close"]
                               })
    return currency_rates, stock_prices


def get_building_response() -> dict[str, str]:
    """
    Сборка всего в единый json ответ
    :return: Словарь с необходимыми данными
    """
    result["greeting"] = get_greeting(datetime.now())
    result["cards"] = get_filtered_operations(DATA_PATH)
    result["top_transactions"] = get_top_operations(DATA_PATH)
    quotes = get_stock_price(datetime.now())
    result["currency_rates"], result["stock_prices"] = quotes[0], quotes[1]
    with open(WRITE_FILE, 'w') as fp:
        json.dump(result, fp, ensure_ascii=False)
    return result


print(get_building_response())
