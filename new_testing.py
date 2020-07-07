# HOTUSDT HOTBTC BTCUSDT
from settings import *
from binance.enums import *
from trade_helper import *
import time


def make_order(symbol: str, side: str, quantity):
    try:
        order = Main.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity)
        return float(order['origQty'])
    except Exception as ex:
        print('ERROR')


qt0 = get_qty_for_trade(get_qty_for_trade(20.0 / last_price, min_qty('HOTUSDT')))
qt1 = make_order(symbol='HOTUSDT', side="BUY", quantity=qt0)

qt2 = make_order(symbol="HOTBTC", side="SELL", quantity=qt1)

qt3 = make_order(symbol="BTCUSDT", side="SELL", quantity=qt2)
