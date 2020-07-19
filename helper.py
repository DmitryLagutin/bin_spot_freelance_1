from settings import *
import datetime


def get_amount(amount, precision):
    return float("{:0.0{}f}".format(amount, precision))


def add_instrument_list(msg):
    """
    Функция, которая добавляет в список иснтрументов все инстременты,
    которые приходят из сокета
    """
    try:
        for i in msg:
            data = dict(symbol=i['s'], event_time=int(i["E"]), last_price=float(i['c']), bid_0=float(i['b']),
                        ask_0=float(i['a']), num_of_trades=float(i['n']) / (24 * 3600))
            list_x = [x for x in Main.instrument_list if x['symbol'] == i['s']]
            if len(list_x) > 0:
                Main.instrument_list.remove(list_x[0])
                if data['num_of_trades'] > 0.2:
                    Main.instrument_list.append(data)
            else:
                if data['num_of_trades'] > 0.2:
                    Main.instrument_list.append(data)
    except Exception as ex:
        print(str(ex))


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


def min_price(ticker):
    """
    Функция, которая выдает минимальную цену, необходимую для торговлия по данному
    инструменту в виде знаков после запятой
    """
    s = str([x["minPrice"] for x in Main.exchange_rules if x['ticker'] == ticker][0]).split('.')
    count = 1
    if s[0] == '1':
        return 0
    else:
        for i in s[1]:
            if i == '1':
                return count
            else:
                count = count + 1


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
            if len(str_x[1]) < y:
                return float('{0}.{1}'.format(str_x[0], str_x[1]))
            else:
                return float('{0}.{1}'.format(str_x[0], str_x[1][0:y]))

    except Exception as ex:
        print(str(ex))


def time_convert(timestamp):
    your_dt = datetime.datetime.fromtimestamp(timestamp / 1000)  # using the local timezone
    return your_dt


def buy_test(symbol, price, qty):
    qty_x = qty / price
    print(symbol, 'BUY---', get_qty_for_trade(qty_x, min_qty(symbol)), min_qty(symbol))
    return qty_x


def sell_test(symbol, price, qty):
    qty_x = qty * price
    print(symbol, 'SELL---', qty_x)
    return qty_x


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
