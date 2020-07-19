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
from peewee import *

db = SqliteDatabase('positionDB.db')


class PositionDB(Model):
    id = TextField()
    qt1 = FloatField(default=0.0)
    qt2 = FloatField(default=0.0)
    qt3 = FloatField(default=0.0)
    trade_level = TextField()

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'


db.connect()
db.create_tables([PositionDB])

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

# основной модуль
while True:
    try:
        # y = [x for x in Main.instrument_list if x['num_of_trades'] > 0.2]
        # print(y)
        # print(len(y))

        print(['{0}-{1}'.format(x['id'], x['delta']) for x in Main.tree_inst_list])
        print(len(Main.tree_inst_list))
        Main.main_tree_object = get_main_inst_tree()
        print('{0} {1} - {2} | {3} {4} - {5} | {6} {7} - {8} | {9}'.format(Main.main_tree_object['first'],
                                                                     Main.main_tree_object['first_val']['bid_0'],
                                                                     Main.main_tree_object['qt1'],
                                                                     Main.main_tree_object['second'],
                                                                     Main.main_tree_object['second_val']['ask_0'],
                                                                     Main.main_tree_object['qt2'],
                                                                     Main.main_tree_object['third'],
                                                                     Main.main_tree_object['third_val']['ask_0'],
                                                                     Main.main_tree_object['qt3'],
                                                                     Main.main_tree_object['delta']))

        # if Main.position is None:
        #     Main.position = Position(instrument_id=Main.main_tree_object['id'])
        # # если позиция создана
        # else:
        #     # если основной инструмент сменился, а в позиции еще не были совршены сделки
        #     if Main.main_tree_object['id'] != Main.position.id and Main.qt1 == 0.0:
        #         Main.position = None
        #     # если основной инструмент тот же или уже были сделки
        #     else:
        #         Main.position.main_func_position()
        # else:
        #     print("Пока что не готовы")

    except Exception as ex:
        print(str(ex))
