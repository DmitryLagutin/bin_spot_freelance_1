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
from trade_helper import *
from settings import *
import time
from instrument_tree import *
import json
from random import randint
import os
import numpy as np
from position import Position

# получить правила биржи
Main.exchange_rules = get_exchange_info(Main.client.get_exchange_info())
# получить ненуливые балансы аккаунта
Main.balance_list = get_balance_list(Main.client.get_account()['balances'])
# получаем тройки для определенного альта
Main.tree_list = make_tree(Main.exchange_rules, 'USDT')

pprint(Main.exchange_rules)

# запускаем все потоки
threading.Thread(target=thread_function).start()
threading.Thread(target=ping_funk).start()


def make_order(symbol: str, side: str, price, quantity):
    try:
        order = Main.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_FOK,  # TIME_IN_FORCE_FOK
            price="{:0.0{}f}".format(price, min_price(symbol)),
            quantity=float("{:0.0{}f}".format(quantity / price, min_qty(symbol)))
            if side == "BUY"
            else float("{:0.0{}f}".format(quantity, min_qty(symbol))))
        if order['status'] == 'FILLED':
            return dict(symbol=order['symbol'], qty=order['origQty'],
                        open_price=order['price'], side=order['side'])
        else:
            return None
    except Exception as ex:
        print(str(ex))
        print('ERROR')


# x1 = []
# x2 = []
# x3 = []
# while len(x1) == 0 or len(x2)== 0 or len(x3)== 0:
#     x1 = [x for x in Main.instrument_list if x['symbol'] == 'HOTUSDT']
#     x2 = [x for x in Main.instrument_list if x['symbol'] == 'HOTBTC']
#     x3 = [x for x in Main.instrument_list if x['symbol'] == 'BTCUSDT']
#
#
# while True:
#     Main.qt2 = make_order(symbol='HOTBTC', side="SELL",
#                           price=float(x2[0]['bid_0']),
#                           quantity=38541)
#     print('Main.qt2', Main.qt2)
#     if Main.qt2 is not None:
#         Main.trade_level.append(1)
#         break


# while True:
#     try:
#
#         x1 = [x for x in Main.instrument_list if x['symbol'] == 'HOTUSDT']
#         x2 = [x for x in Main.instrument_list if x['symbol'] == 'HOTBTC']
#         x3 = [x for x in Main.instrument_list if x['symbol'] == 'BTCUSDT']
#         if len(Main.trade_level) == 0:
#             Main.qt1 = make_order(symbol='HOTUSDT', side="BUY",
#                                   price=float(x1[0]['bid_0']),
#                                   quantity=30.0)
#             print('Main.qt1', Main.qt1)
#             if Main.qt1 is not None:
#                 Main.trade_level.append(1)
#
#         elif len(Main.trade_level) == 1:
#             Main.qt2 = make_order(symbol='HOTBTC', side="SELL",
#                                   price=float(x2[0]['ask_0']),
#                                   quantity=Main.qt1['qty'])
#             print('Main.qt2', Main.qt2)
#             if Main.qt2 is not None:
#                 Main.trade_level.append(1)
#         elif len(Main.trade_level) == 2:
#             Main.qt3 = make_order(symbol='HOTUSDT', side="SELL",
#                                   price=float(x3[0]['bid_0']),
#                                   quantity=Main.qt2['qty'])
#             print('Main.qt3', Main.qt3)
#             if Main.qt3 is not None:
#                 Main.trade_level.append(1)
#
#         if len(Main.trade_level) == 3:
#             print(Main.qt1, Main.qt2, Main.qt3)
#             break
#
#
#     except Exception as ex:
#         print(str(ex))


# основной модуль
while True:
    try:
        # получаем иснтрумент с самым большим матиматическим ожиданием, исходя из условий, а также список иструментов
        main_instrument_tree, main_list_x = get_main_instrument_tree(first_balance=100.0,
                                                                     more_that=50.0,
                                                                     seconds_delta=10,
                                                                     exchange_rates=70.0)
        print(['{0}-{1}'.format(x.id, x.delta) for x in main_list_x])
        if main_instrument_tree is not None:
            print(main_instrument_tree.first, main_instrument_tree.second, main_instrument_tree.third,
                  main_instrument_tree.delta, '{0} - количество'.format(len(main_list_x)))
            # print(main_instrument.delta_0)
            zz = (datetime.datetime.now() - time_convert(main_instrument_tree.min_event_time))
            print(zz.seconds)

            # # если позиция пока что не создана
            # if Main.position is None:
            #     Main.position = Position(instrument_id=main_instrument_tree.id)
            # # если позиция создана
            # else:
            #     # если основной инструмент сменился, а в позиции еще не были совршены сделки
            #     if main_instrument_tree.id != Main.position.id and Main.qt1 == 0.0:
            #         Main.position = None
            #     # если основной инструмент тот же или уже были сделки
            #     else:
            #         Main.position.main_func_position()
        else:
            print("Пока что не готовы")

        # time.sleep(1)
    except Exception as ex:
        print(str(ex))
