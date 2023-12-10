from dotenv import load_dotenv
from datetime import timedelta, datetime
from typing import Any, List, Dict
import pandas as pd
import requests
import os
import logging

from pandas import DataFrame

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")


def get_data(path: str) -> DataFrame | Exception:
    """
    Возвращает датафрейм из файла
    :param path: путь к файлу
    :return: датафрейм
    """
    try:
        operations = pd.read_excel(path, date_format="%d.%m.%Y %H:%M:%S", parse_dates=["Дата операции"]).dropna(
            subset=['Номер карты'])
        logger.info("get_data successfully")
        return operations
    except Exception as error:
        logger.error(f"get_data: {error}")
        return error


def get_greeting(date: Any) -> str:
    """
    Приветствие
    :param date: Дата
    :return: Приветствие
    """
    try:
        opts = ['Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи']
        if 4 < date.hour <= 12:
            logger.info("get_greeting successfully")
            return opts[0]
        elif 12 < date.hour <= 16:
            logger.info("get_greeting successfully")
            return opts[1]
        elif 16 < date.hour <= 24:
            logger.info("get_greeting successfully")
            return opts[2]
        else:
            logger.info("get_greeting successfully")
            return opts[3]
    except Exception as error:
        logger.error(f"get_data: {error}")
        return ""


def get_filtered_operations(path: str) -> list[dict[str, int | Any]] | dict[str, Exception]:
    """
    Чтение финансовых операций с CSV- и XLS-файлов
    :param path: Путь до файла
    :return: DataFrame всех операций
    """
    try:
        operations = get_data(path)
        cards = [{"last_digits": number_card, "total_spent": 0, "cashback": 0} for number_card in
                 operations['Номер карты'].unique()]
        for card in cards:
            filtered_operations = operations.loc[
                (operations["Номер карты"] == card["last_digits"]) & (operations["Статус"] == "OK") & (
                    operations['Сумма операции'] <= 0)]
            card["total_spent"] = round(abs(filtered_operations['Сумма операции'].sum()), 2)
            card["cashback"] = round(card["total_spent"] / 100)
        logger.info("get_filtered_operations successfully")
        return cards
    except Exception as error:
        logger.error(f"get_filtered_operations: {error}")
        return {"error": error}


def get_top_operations(path: str) -> list[dict[str, int | Any]] | dict[str, Exception]:
    """
    Топ 5 самых больших расходов
    :param path: путь чтения файла
    :return: Словари с информацией
    """
    try:
        operations = get_data(path)
        filtered_operations = operations.loc[(operations["Статус"] == "OK") & (
            operations['Сумма операции'] <= 0)]
        top_max_operations = [{"date": str(operation["Дата операции"]),
                               "amount": abs(operation["Сумма операции"]),
                               "category": operation["Категория"],
                               "description": operation["Описание"]} for operation in
                              filtered_operations.sort_values(by='Сумма операции')[:5].to_dict("records")]
        logger.info("get_top_operations successfully")
        return top_max_operations
    except Exception as error:
        logger.error(f"get_top_operations: {error}")
        return {"error": error}


def get_stock_price(date: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | list[Any]:
    """
    Курс акции за вчерашний торговый день
    :param date: Дата
    :return: Словарь с вчерашними ценами закрытия {MSFT: 123, и т.д.}
    """
    try:
        stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        currencies = ["USD", "EUR"]
        stock_prices = []
        currency_rates = []
        yesterday = (date - timedelta(days=1)).strftime("%Y-%m-%d")
        for stock in stocks:
            url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&outputsize=compact'
                   f'&apikey={API_KEY}')
            response = requests.get(url).json()
            stock_prices.append({"stock": response["Meta Data"]["2. Symbol"],
                                 "price": response["Time Series (Daily)"][yesterday]["4. close"]})
        for currency in currencies:
            url = (f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={currency}'
                   f'&to_symbol=RUB&apikey={API_KEY}')
            response = requests.get(url).json()
            currency_rates.append({"currency": response["Meta Data"]["2. From Symbol"],
                                   "rate": response["Time Series FX (Daily)"][yesterday]["4. close"]
                                   })
        logger.info("get_stock_price successfully")
        return [currency_rates, stock_prices]
    except Exception as error:
        logger.error(f"get_stock_price: {error}")
        return []


def building_json_views(date: str, data_path: str) -> dict[str, Any] | Any:
    """
    Создает словарь с данными
    :param date: дата
    :param data_path: путь файла с данными
    :return: словарь
    """
    result = {}
    date_obj = datetime.now() if not date else datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    result["greeting"] = get_greeting(date_obj)
    result["cards"] = get_filtered_operations(data_path)
    result["top_transactions"] = get_top_operations(data_path)
    quotes = get_stock_price(date_obj)
    if not quotes:
        result["currency_rates"], result["stock_prices"] = None, None
    else:
        result["currency_rates"], result["stock_prices"] = quotes[0], quotes[1]
    return result
