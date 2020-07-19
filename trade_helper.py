from pprint import pformat
from decimal import *
from helper import *
# from helper import min_qty
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
from settings import Main


def thread_function():
    """
    Функция, которая запускает все основные потоки
    """
    bm = BinanceSocketManager(Main.client)
    bm.start_ticker_socket(add_instrument_list)
    bm.start_user_socket(user_socket)
    bm.start()


def make_main_tree_list(first_balance, more_that, exchange_rates):
    while True:
        for i in Main.tree_list:
            make_main_list(first=i['first'],
                           second=i['second'],
                           third=i['third'],
                           first_balance=first_balance,
                           more_that=more_that,
                           exchange_rates=exchange_rates)


def user_socket(msg):
    """
    Сокет, из которого мы получаем данные юзера Бинанс
    """
    if msg['e'] == 'executionReport':
        Main.main_order = dict(orderId=msg['i'], symbol=msg['s'], qty=msg['q'],
                               open_price=msg['p'], side=msg['S'], status=msg['x'])
        pass
    elif msg['e'] == 'outboundAccountInfo':
        Main.balance_list = get_balance_list_socket(msg['B'])
    elif msg['e'] == 'outboundAccountPosition':
        pass


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
    list_result_z = []
    quote_ass_list = [x for x in main_list if x['quoteAss'] == symbol_ass]
    base_ass_list = [x['baseAss'] for x in quote_ass_list]
    base_ass_list_copy = base_ass_list
    for i in base_ass_list:
        for j in base_ass_list_copy:
            if i != j:
                list_result.append(dict(first=i + symbol_ass,
                                        second=i + j,
                                        third=j + symbol_ass,
                                        id=i + symbol_ass + i + j + j + symbol_ass))
                list_result.append(dict(first=j + symbol_ass,
                                        second=i + j,
                                        third=i + symbol_ass,
                                        id=j + symbol_ass + i + j + i + symbol_ass))
                list_result.append(dict(first=i + symbol_ass,
                                        second=j + i,
                                        third=j + symbol_ass,
                                        id=i + symbol_ass + j + i + j + symbol_ass))
                list_result.append(dict(first=j + symbol_ass,
                                        second=j + i,
                                        third=i + symbol_ass,
                                        id=j + symbol_ass + j + i + i + symbol_ass))

    for i in list_result:
        if i['first'] in [x['ticker'] for x in main_list] \
                and i['second'] in [x['ticker'] for x in main_list] \
                and i['third'] in [x['ticker'] for x in main_list]:
            list_result_y.append(i)
    for i in list_result_y:
        if i['id'] not in [x['id'] for x in list_result_z]:
            list_result_z.append(i)
    return list_result_z


def get_qty_for_trade(odj, y: int):
    """
    Функция, которая выдает объем оптимальный для торгов в соотвествии с правилами
    """
    str_x = str(odj).split('.')
    try:
        if y == 0:
            return float('{0}.{1}'.format(str_x[0], str(y)))
        else:
            if len(str_x[1]) < y:
                return float('{0}.{1}'.format(str_x[0], str_x[1]))
            else:
                return float('{0}.{1}'.format(str_x[0], str_x[1][0:y]))

    except Exception as ex:
        print(str(ex))


def get_main_inst_tree():
    if len(Main.tree_inst_list) > 0:
        max_delta = sorted([x['delta'] for x in Main.tree_inst_list])[-1]
        return [x for x in Main.tree_inst_list if x['delta'] == max_delta][0]
    else:
        return None


def check_None(if_x):
    list_x = [x for x in Main.instrument_list if x['symbol'] == if_x]
    if len(list_x) > 0:
        return list_x[0]
    else:
        return None


def make_main_list(first, second, third, first_balance: float, more_that: float, exchange_rates: float):
    dict_x = {}
    try:
        dict_x['id'] = first + second + third
        dict_x['first'] = first
        dict_x['second'] = second
        dict_x['third'] = third
        dict_x['first_val'] = check_None(first)
        dict_x['second_val'] = check_None(second)
        dict_x['third_val'] = check_None(third)
        list_x = [dict_x['first_val'], dict_x['second_val'], dict_x['third_val']]
        if None not in list_x:
            dict_x['first_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == first][0]
            dict_x['second_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == second][0]
            dict_x['third_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == third][0]

            # xxx = float(dict_x['first_val']['bid_0'])  # - 0 * float(dict_x['first_symbol_rule']['minPrice'])
            qt1 = get_amount(first_balance / float(dict_x['first_val']['bid_0']), min_qty(dict_x['first']))
            dict_x['qt1'] = qt1
            qt2 = 0.0
            if dict_x['first_symbol_rule']['baseAss'] == dict_x['second_symbol_rule']['quoteAss']:
                qt2 = get_amount(qt1 / dict_x['second_val']['ask_0'], min_qty(dict_x['second']))
                dict_x['qt2'] = qt2
            elif dict_x['first_symbol_rule']['baseAss'] == dict_x['second_symbol_rule']['baseAss']:
                qt2 = get_amount(qt1 * dict_x['second_val']['ask_0'], min_qty(dict_x['second']))
                dict_x['qt2'] = qt2
            # yyy = float(dict_x['third_val']['ask_0'])  # + 0 * float(dict_x['third_symbol_rule']['minPrice'])
            qt3 = get_amount(qt2 * float(dict_x['third_val']['ask_0']), min_qty(dict_x['third']))
            dict_x['qt3'] = qt3
            delta = qt3 - first_balance

            comission = (first_balance * 0.075 / 100) * 3
            dict_x['delta'] = (delta - comission) * exchange_rates

            list_cc = [x for x in Main.tree_inst_list if x['id'] == dict_x['id']]
            if len(list_cc) > 0:
                Main.tree_inst_list.remove(list_cc[0])
                if dict_x['delta'] > more_that:
                    Main.tree_inst_list.append(dict_x)
            else:
                if dict_x['delta'] > more_that:
                    Main.tree_inst_list.append(dict_x)
    except Exception as ex:
        print('ere')
        print(str(ex))

# def trade(symbol, side,  price: float, qty : float):
#     def make_order(symbol: str, side: str, price, quantity):
#         try:
#             order = Main.client.create_order(
#                 symbol=symbol,
#                 side=side,
#                 type=ORDER_TYPE_LIMIT,
#                 timeInForce=TIME_IN_FORCE_GTC,
#                 price=price,
#                 quantity=quantity)
#             return dict(order=order, status=order[])
#         except Exception as ex:
#             print(str(ex))
#             print('ERROR')
#
#
#
#     if Main.order is None:
#         Main.order = make_order(symbol=symbol, side=side,
#                                 price=price,
#                                 quantity=qty)
#         if Main.order['status'] == 'FILLED':
#             return Main.order
#     else:
#         if Main.order
#         if price != Main.order['price'] or qty != Main.order['origQty']:
#             result = Main.client.cancel_order(symbol=symbol, orderId=Main.order['orderId'])
#             if result['status'] == "CANCELED":
#                 Main.order = None
