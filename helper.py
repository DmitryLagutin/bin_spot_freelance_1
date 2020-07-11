from settings import *
import datetime


def add_instrument_list(msg):
    """
    Функция, которая добавляет в список иснтрументов все инстременты,
    которые приходят из сокета
    """
    try:
        for i in msg:
            data = dict(symbol=i['s'], event_time=int(i["E"]), last_price=float(i['c']), bid_0=float(i['b']),
                        ask_0=float(i['a']), num_of_trades=float(i['n']))
            list_x = [x for x in Main.instrument_list if x['symbol'] == i['s']]
            if len(list_x) > 0:
                Main.instrument_list.remove(list_x[0])
                Main.instrument_list.append(data)
            else:
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



def make_instrument_dict(first, second, third, first_balance: float, exchange_rates: float):
    dict_x = {}
    dict_x['id'] = first['symbol'] + second['symbol'] + third['symbol']
    dict_x['first'] = first['symbol']
    dict_x['second'] = second['symbol']
    dict_x['third'] = third['symbol']
    dict_x['first_val'] = first
    dict_x['second_val'] = second
    dict_x['third_val'] = third

    dict_x['first_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == first['symbol']][0]
    dict_x['second_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == second['symbol']][0]
    dict_x['third_symbol_rule'] = [x for x in Main.exchange_rules if x['ticker'] == third['symbol']][0]

    xxx = float(dict_x['first_val']['bid_0']) - 0 * float(dict_x['first_symbol_rule']['minPrice'])

    qt1 = float("{:0.0{}f}".format(first_balance / xxx, min_qty(dict_x['first'])))
    qt2 = 0.0
    if dict_x['first_symbol_rule']['baseAss'] == dict_x['second_symbol_rule']['quoteAss']:
        qt2 = float("{:0.0{}f}".format(qt1 / dict_x['second_val']['bid_0'], min_qty(dict_x['second'])))
    elif dict_x['first_symbol_rule']['baseAss'] == dict_x['second_symbol_rule']['baseAss']:
        qt2 = float("{:0.0{}f}".format(qt1 * dict_x['second_val']['ask_0'], min_qty(dict_x['second'])))

    yyy = float(dict_x['third_val']['ask_0']) + 0 * float(dict_x['third_symbol_rule']['minPrice'])
    qt3 = float("{:0.0{}f}".format(qt2 * yyy, min_qty(dict_x['third'])))
    delta = qt3 - first_balance

    comission = (first_balance * 0.075 / 100) * 3
    dict_x['delta'] = (delta - comission) * exchange_rates

    dict_x['min_event_time'] = sorted([dict_x['first_val']['event_time'],
                                       dict_x['second_val']['event_time'],
                                       dict_x['third_val']['event_time']])[0]

    dict_x['num_of_trades'] = sorted([dict_x['first_val']['num_of_trades'],
                                      dict_x['second_val']['num_of_trades'],
                                      dict_x['third_val']['num_of_trades']])[0] / (24 * 3600)

    return dict_x