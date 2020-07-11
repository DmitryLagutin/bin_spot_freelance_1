from pprint import pformat
from decimal import *
from helper import *
from instrument_tree import InstrumentTree
from settings import *
from decimal import *
from typing import List, Any

from binance.websockets import BinanceSocketManager
from binance.client import Client
import threading
import ast
from time import sleep
from binance.enums import *
from pprint import pprint
from binance.client import Client
import datetime
from instrument_tree import *


def thread_function():
    """
    Функция, которая запускает все основные потоки
    """
    bm = BinanceSocketManager(Main.client)
    bm.start_ticker_socket(add_instrument_list)
    bm.start_user_socket(user_socket)
    bm.start()


def user_socket(msg):
    """
    Сокет, из которого мы получаем данные юзера Бинанс
    """
    if msg['e'] == 'executionReport':
        pass
    elif msg['e'] == 'outboundAccountInfo':
        Main.balance_list = get_balance_list_socket(msg['B'])
    elif msg['e'] == 'outboundAccountPosition':
        pass


def ping_funk():
    """
    Функиця, которая в отдельном потоке пингует сервер
    Бинанс
    """
    while True:
        Main.client.ping()
        sleep(600)


def get_exchange_info(dict_list: dict):
    """
    Функция, которая создает список правил биржы
    """
    return_list = []
    for i in dict_list['symbols']:
        dict_ex = dict(ticker=i['symbol'],
                       baseAss=i['baseAsset'],
                       quoteAss=i['quoteAsset'],
                       minQty=[x for x in i['filters'] if x['filterType'] == 'LOT_SIZE'][0]['minQty'],
                       stepSize=[x for x in i['filters'] if x['filterType'] == 'LOT_SIZE'][0]['stepSize'],
                       minPrice=[x for x in i['filters'] if x['filterType'] == 'PRICE_FILTER'][0]['minPrice'],
                       tickSize=[x for x in i['filters'] if x['filterType'] == 'PRICE_FILTER'][0]['tickSize'])
        return_list.append(dict_ex)
    return return_list


def get_balance_list(dict_x: dict):
    """
    Получаем список с балансами в кошельке
    """
    list_x = []
    not_null_balance_list = [x for x in dict_x if float(x['free']) > 0 or float(x['locked']) > 0]
    for balance in not_null_balance_list:
        list_x.append(dict(asset=balance['asset'], free=balance['free'],
                           locked=balance['locked']))
    return list_x


def make_tree(main_list: list, symbol_ass: str):
    """
    Создаем тройки пар, из которых потом будем искать выгодные комбинации
    """
    list_result = []
    list_result_y = []
    quote_ass_list = [x for x in main_list if x['quoteAss'] == symbol_ass]
    base_ass_list = [x['baseAss'] for x in quote_ass_list]
    base_ass_list_copy = base_ass_list
    for i in base_ass_list:
        for j in base_ass_list_copy:
            if i != j:
                list_result.append(dict(first=i + symbol_ass,
                                        second=i + j,
                                        third=j + symbol_ass))
                list_result.append(dict(first=j + symbol_ass,
                                        second=i + j,
                                        third=i + symbol_ass))
                list_result.append(dict(first=i + symbol_ass,
                                        second=j + i,
                                        third=j + symbol_ass))
                list_result.append(dict(first=j + symbol_ass,
                                        second=j + i,
                                        third=i + symbol_ass))

    for i in list_result:
        if i['first'] in [x['ticker'] for x in main_list] \
                and i['second'] in [x['ticker'] for x in main_list] \
                and i['third'] in [x['ticker'] for x in main_list]:
            list_result_y.append(i)
    return list_result_y


def get_main_instrument_tree(first_balance: float, more_that: float, num_of_trades: float, exchange_rates: float):
    def make_tree_instrument():
        """ Создаем список объектов класса Instrument,
        который в дальнейшем испрользуется для работы """
        Main.tree_inst_list = []

        try:
            def get_x(symbol):
                try:
                    return [x for x in Main.instrument_list if x['symbol'] == symbol][0]
                except Exception as ex:
                    return None

            for tree_x in Main.tree_list:
                if get_x(tree_x['first']) is not None \
                        and get_x(tree_x['second']) is not None \
                        and get_x(tree_x['third']) is not None:
                    if tree_x['first'] + \
                            tree_x['second'] + \
                            tree_x['third'] not in [x['id'] for x in Main.tree_inst_list]:
                        Main.tree_inst_list.append(make_instrument_dict(first=get_x(tree_x['first']),
                                                                        second=get_x(tree_x['second']),
                                                                        third=get_x(tree_x['third']),
                                                                        first_balance=first_balance,
                                                                        exchange_rates=exchange_rates))

        except Exception as ex:
            print(str(ex))
            print('Ошибка в make_tree_instrument')

    """
    Получает самую главную тройку, который состоит из трех иструментов, которые соотвествуют
    условиям
    """
    main_instrument_result = None
    list_xx = []
    try:
        # пересчитываем все тройки инструментов
        make_tree_instrument()

        list_xx = [x for x in Main.tree_inst_list if
                   x['delta'] > more_that
                   and x['num_of_trades'] > num_of_trades]

        if len(list_xx) > 1:
            max_delta = sorted([x['delta'] for x in list_xx])[-1]
            main_instrument_result = [x for x in list_xx if x['delta'] == max_delta][0]
    except Exception as ex:
        print('Ошибка в get_main_instrument')
    finally:
        return main_instrument_result, list_xx



