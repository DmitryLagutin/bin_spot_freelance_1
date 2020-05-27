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
import json
from random import randint
import os

# получить правила биржи
Main.exchange_rules = get_exchange_info(Main.client.get_exchange_info())
# получить ненуливые балансы аккаунта
Main.balance_list = make_account_info_client(Main.client.get_account()['balances'])
# получить свободный баланс базового символа
Main.balance = [x for x in Main.balance_list if x['asset'] == Main.basic_symbol][0]['free']

# запускаем все потоки
threading.Thread(target=thread_function).start()
threading.Thread(target=ping_funk).start()

# основной модуль
while True:
    try:

        price1 = (get_ticker("BTCUSDT")['bid_0'] - float(100))
        result = make_order(Main.client, "BUY", 'BTCUSDT', float(Main.balance) / price1, price1)

    except Exception as ex:
        print(str(ex))
