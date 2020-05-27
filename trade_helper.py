from pprint import pformat
from decimal import *
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


def thread_function():
    bm = BinanceSocketManager(Main.client)
    bm.start_ticker_socket(add_main_list_ticker)
    bm.start_user_socket(user_socket)
    bm.start()


def add_main_list_ticker(msg):
    try:
        for i in msg:
            data = dict(symbol=i['s'], last_price=float(i['c']), bid_0=float(i['b']), ask_0=float(i['a']))
            list_x = [x for x in Main.main_list_ticker if x['symbol'] == i['s']]
            if len(list_x) > 0:
                Main.main_list_ticker.remove(list_x[0])
                Main.main_list_ticker.append(data)
            else:
                Main.main_list_ticker.append(data)
    except Exception as ex:
        print(str(ex))


def user_socket(msg):
    if msg['e'] == 'executionReport':
        pass
    elif msg['e'] == 'outboundAccountInfo':
        Main.balance_list = make_account_info_socket(msg['B'])
    elif msg['e'] == 'outboundAccountPosition':
        Main.balance_list_instrument = make_account_info_instrument_balance_socket(msg['B'])


def ping_funk():
    while True:
        print(Main.client.ping())
        sleep(600)


def get_count(ticker, min_amount):
    s = str([x[min_amount] for x in Main.exchange_rules if x['ticker'] == ticker][0]).split('.')
    count = 1
    for i in s[1]:
        if i == '1':
            return count
        else:
            count = count + 1


def get_exchange_info(dict_list: dict):
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


def make_account_info_client(dict_x: dict):
    list_x = []
    not_null_balance_list = [x for x in dict_x if float(x['free']) > 0 or float(x['locked']) > 0]
    for balance in not_null_balance_list:
        list_x.append(dict(asset=balance['asset'], free=balance['free'],
                           locked=balance['locked']))
    return list_x


def get_qty_for_trade(odj, y: int):
    str_x = str(odj).split('.')
    try:
        return float('{0}.{1}'.format(str_x[0], str_x[1][0:y]))
    except Exception as ex:
        print(str(ex))


def make_account_info_socket(dict_x: dict):
    list_x = []
    not_null_balance_list = [x for x in dict_x if float(x['f']) > 0 or float(x['l']) > 0]
    for balance in not_null_balance_list:
        list_x.append(dict(asset=balance['a'], free=balance['f'],
                           locked=balance['l']))
    return list_x


def make_account_info_instrument_balance_socket(dict_x: dict):
    list_x = []
    for balance in dict_x:
        list_x.append(dict(asset=balance['a'], free=balance['f'],
                           locked=balance['l']))
    return list_x


def get_ticker(ticker: str):
    list_x = [x for x in Main.main_list_ticker if x['symbol'] == ticker]

    if len(list_x) > 0:
        return list_x[0]
    else:
        return dict(symbol="None", last_price=float(0), bid_0=float(0), ask_0=float(0))


def make_order(client: Client, side: str, ticker: str, quantity, price):
    side_x = SIDE_BUY if side == "BUY" else SIDE_SELL
    price = get_qty_for_trade(price, get_count(ticker=ticker, min_amount='minPrice'))
    quantity = get_qty_for_trade(quantity, get_count(ticker=ticker, min_amount='minQty'))
    try:
        order = client.create_order(
            symbol=ticker,
            side=side_x,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_FOK,  # TIME_IN_FORCE_FOK
            quantity=quantity,
            price=str(price))
        print(order)
        return order
    except Exception as ex:
        # print(str(ex), '-----------')
        return 'ERROR'
