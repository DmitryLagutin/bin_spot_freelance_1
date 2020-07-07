from pprint import pformat
from decimal import *

from instrument import Instrument
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
from instrument import *


def thread_function():
    """
    Функция, которая запускает все основные потоки
    """
    bm = BinanceSocketManager(Main.client)
    bm.start_ticker_socket(add_instrument_list)
    bm.start_user_socket(user_socket)
    bm.start()


def add_instrument_list(msg):
    """
    Функция, которая добавляет в список иснтрументов все инстременты,
    которые приходят из сокета
    """
    try:
        for i in msg:
            data = dict(symbol=i['s'], last_price=float(i['c']), bid_0=float(i['b']), ask_0=float(i['a']))
            list_x = [x for x in Main.instrument_list if x['symbol'] == i['s']]
            if len(list_x) > 0:
                Main.instrument_list.remove(list_x[0])
                Main.instrument_list.append(data)
            else:
                Main.instrument_list.append(data)
    except Exception as ex:
        print(str(ex))


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
        # Main.balance_list_instrument = make_account_info_instrument_balance_socket(msg['B'])


def ping_funk():
    """
    Функиця, которая в отдельном потоке пингует сервер
    Бинанс
    """
    while True:
        Main.client.ping()
        sleep(600)


def get_count(ticker, min_amount):
    """
    Функиця, которая получает количество знаков после запятой
    """
    s = str([x[min_amount] for x in Main.exchange_rules if x['ticker'] == ticker][0]).split('.')
    count = 1
    for i in s[1]:
        if i == '1':
            return count
        else:
            count = count + 1


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


def min_qty(ticker):
    """
    Функция, которая выдает минимальный объем, необходимый для торговлия по данному
    инструменту в виде знаков после запятой
    """
    s = str([x["minQty"] for x in Main.exchange_rules if x['ticker'] == ticker][0]).split('.')
    count = 1
    if s[0] == '1':
        return 0
    else:
        for i in s[1]:
            if i == '1':
                return count
            else:
                count = count + 1


def get_qty_for_trade(odj, y: int):
    """
    Функция, которая выдает объем оптимальный для торгов в соотвествии с правилами
    """
    str_x = str(odj).split('.')
    try:
        if y == 0:
            return float('{0}.{1}'.format(str_x[0], str(y)))
        else:
            return float('{0}.{1}'.format(str_x[0], str_x[1][0:y]))
    except Exception as ex:
        print(str(ex))


def get_balance_list_socket(dict_x: dict):
    """
    Получаем список с балансами в кошельке из сокета
    """
    list_x = []
    not_null_balance_list = [x for x in dict_x if float(x['f']) > 0 or float(x['l']) > 0]
    for balance in not_null_balance_list:
        list_x.append(dict(asset=balance['a'], free=balance['f'],
                           locked=balance['l']))
    return list_x


# def make_account_info_instrument_balance_socket(dict_x: dict):
#     list_x = []
#     for balance in dict_x:
#         list_x.append(dict(asset=balance['a'], free=balance['f'],
#                            locked=balance['l']))
#     return list_x


# def make_order(client: Client, side: str, ticker: str, quantity, price):
#     side_x = SIDE_BUY if side == "BUY" else SIDE_SELL
#     price = get_qty_for_trade(price, get_count(ticker=ticker, min_amount='minPrice'))
#     quantity = get_qty_for_trade(quantity, get_count(ticker=ticker, min_amount='minQty'))
#     try:
#         order = client.create_order(
#             symbol=ticker,
#             side=side_x,
#             type=ORDER_TYPE_LIMIT,
#             timeInForce=TIME_IN_FORCE_FOK,  # TIME_IN_FORCE_FOK
#             quantity=quantity,
#             price=str(price))
#         print(order)
#         return order
#     except Exception as ex:
#         # print(str(ex), '-----------')
#         return 'ERROR'


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
            if get_x(tree_x['first']) is not None and get_x(tree_x['second']) is not None and get_x(
                    tree_x['third']) is not None:
                Main.tree_inst_list.append(Instrument(
                    first=tree_x['first'], first_val=get_x(tree_x['first']),
                    second=tree_x['second'], second_val=get_x(tree_x['second']),
                    third=tree_x['third'], third_val=get_x(tree_x['third'])
                ))
    except Exception as ex:
        print('Ошибка в make_tree_instrument')


def get_main_instrument(first_balance: float, more_that: float, exchange_rates: float):
    """
    Получает самую главную тройку, который состоит из трех иструментов, которые соотвествуют
    условиям
    """
    main_instrument_result = None
    list_xx = []
    try:
        make_tree_instrument()
        for i in Main.tree_inst_list:
            i.get_delta(first_balance=first_balance, exchange_rates=exchange_rates)

        list_xx = [x for x in Main.tree_inst_list if x.delta > more_that]
        if len(list_xx) > 1:
            max_delta = sorted([x.delta for x in list_xx])[-1]
            main_instrument_result = [x for x in list_xx if x.delta == max_delta][0]
    except Exception as ex:
        print('Ошибка в get_main_instrument')
    finally:
        return main_instrument_result, list_xx
