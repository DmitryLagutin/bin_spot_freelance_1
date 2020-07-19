from decimal import *
from pathlib import Path
import random
from typing import List, Any
from binance.websockets import BinanceSocketManager
from binance.client import Client
import threading
import ast
from time import sleep
from binance.enums import *
from pprint import pprint
from helper import *
from trade_helper import *
from settings import *
import time
from instrument_tree import *
import json
from random import randint
import os
from position import Position


# получить правила биржи
Main.exchange_rules = get_exchange_info(Main.client.get_exchange_info())
# получить ненуливые балансы аккаунта
Main.balance_list = get_balance_list(Main.client.get_account()['balances'])
# получаем тройки для определенного альта
Main.tree_list = make_tree(Main.exchange_rules, 'USDT')

# запускаем все потоки
threading.Thread(target=thread_function).start()
# args [first_balance, more_that, exchange_rates]
threading.Thread(target=make_main_tree_list, args=[15.0, 0.0, 70.0]).start()


def get_amount(amount, precision):
    return float("{:0.0{}f}".format(amount, precision))


def make_order(symbol: str, side: str, price, quantity):
    try:
        order = Main.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_FOK,  # TIME_IN_FORCE_FOK
            price=price,
            quantity=get_amount(quantity, min_qty(symbol)))
        if order['status'] == 'FILLED':
            print(order)
            if side == "SELL":
                return dict(orderId=order['orderId'], symbol=order['symbol'],
                            qty_org=order['origQty'],
                            qty_fills=float(order['fills'][0]['qty']) * float(order['price']),
                            open_price=order['price'], side=order['side'], status=order['status'])
            else:
                return dict(orderId=order['orderId'], symbol=order['symbol'],
                            qty_org=order['origQty'],
                            qty_fills=float(order['fills'][0]['qty']),
                            open_price=order['price'], side=order['side'], status=order['status'])

        else:
            return None
    except Exception as ex:
        print(str(ex))
        print('ERROR')


x1 = []
x2 = []
x3 = []
while len(x1) == 0 or len(x2) == 0 or len(x3) == 0:
    x1 = [x for x in Main.instrument_list if x['symbol'] == 'ETHUSDT']
    x2 = [x for x in Main.instrument_list if x['symbol'] == 'ETHBTC']
    x3 = [x for x in Main.instrument_list if x['symbol'] == 'BTCUSDT']


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


while True:
    try:

        # print(Main.main_order, '------------')
        # x1 = [x for x in Main.instrument_list if x['symbol'] == 'ETHUSDT']
        # x2 = [x for x in Main.instrument_list if x['symbol'] == 'ETHBTC']
        # x3 = [x for x in Main.instrument_list if x['symbol'] == 'BTCUSDT']

        if len(Main.trade_level) == 0:
            Main.qt1 = make_order(symbol='ETHUSDT', side="BUY",
                                  price=float(x1[0]['bid_0']),
                                  quantity=15.0 / float(x1[0]['bid_0']))

            print('Main.qt1', Main.qt1, float(x1[0]['bid_0']))
            if Main.qt1 is not None:
                Main.trade_level.append(1)

        elif len(Main.trade_level) == 1:
            Main.qt2 = make_order(symbol='ETHBTC', side="SELL",
                                  price=float(x2[0]['ask_0']),
                                  quantity=Main.qt1['qty_fills'])
            print('Main.qt2', Main.qt2, float(x2[0]['ask_0']))
            if Main.qt2 is not None:
                Main.trade_level.append(1)
        elif len(Main.trade_level) == 2:
            Main.qt3 = make_order(symbol='BTCUSDT', side="SELL",
                                  price=float(x3[0]['ask_0']),
                                  quantity=Main.qt2['qty_fills'])
            print('Main.qt3', Main.qt3, float(x3[0]['ask_0']))
            if Main.qt3 is not None:
                Main.trade_level.append(1)

        if len(Main.trade_level) == 3:
            print(Main.qt1, Main.qt2, Main.qt3)
            break


    except Exception as ex:
        print(str(ex))

# while True:
#     x1 = [x for x in Main.instrument_list if x['symbol'] == 'BTCUSDT']
#     if len(x1) > 0:
#         price1 = float(x1[0]['bid_0']) - 100.00
#         order = make_order(symbol='BTCUSDT', side='BUY',
#                            price=price1, quantity=15.0 / price1)
#         print(order)
#     else:
#         print("Пока что нет")
