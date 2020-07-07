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
from instrument import *
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

# запускаем все потоки
threading.Thread(target=thread_function).start()
threading.Thread(target=ping_funk).start()

time.sleep(5)


def make_order(symbol: str, side: str, quantity):
    try:
        order = Main.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity)
        return float(order['origQty']), order
    except Exception as ex:
        print(str(ex))
        print('ERROR')


x = []
while len(x) == 0:
    x = [x['ask_0'] for x in Main.instrument_list if x['symbol'] == 'HOTUSDT']

qt1, order1 = make_order(symbol='HOTUSDT', side="BUY",
                         quantity=get_qty_for_trade(30.0 / x[0], min_qty('HOTUSDT')))
print(order1)
time.sleep(1)
qt2, order2 = make_order(symbol="HOTBTC", side="SELL",
                         quantity=qt1)
print(order2)
time.sleep(1)
qt3, order3 = make_order(symbol="BTCUSDT", side="SELL",
                         quantity=get_qty_for_trade(qt2, min_qty('BTCUSDT')))
print(order3)
print("Все готово")
print(30.0, qt1, qt2, qt3)
print('---------')
print(order1, order2, order3)

# # основной модуль
# while True:
#     try:
#         # получаем иснтрумент с самым большим матиматическим ожиданием, исходя из условий, а также список иструментов
#         main_instrument, main_list_x = get_main_instrument(first_balance=100.0,
#                                                            more_that=100.0,
#                                                            exchange_rates=70.0)
#         if main_instrument is not None:
#             print(main_instrument.first, main_instrument.second, main_instrument.third,
#                   main_instrument.delta, '{0} - количество'.format(len(main_list_x)))
#             # если позиция пока что не создана
#             if Main.position is None:
#                 Main.position = Position(instrument_id=main_instrument.id)
#             # если позиция создана
#             else:
#                 Main.position.main_func_position()
#         else:
#             print("Пока что не готовы")
#
#         # time.sleep(1)
#     except Exception as ex:
#         print(str(ex))
