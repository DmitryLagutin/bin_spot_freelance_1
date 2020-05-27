from binance.client import Client


class Main:
    # клиент
    client = Client('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    # правила биржи
    exchange_rules = []
    # базовый символ
    basic_symbol = 'USDT'
    # базовый баланс
    balance = float(0)
    # список свободных балансов
    balance_list = []
    # основной ордер в данный момент
    order_main = None
    # основной список тикеров
    main_list_ticker = []
    # основной список позиций
    instrument_list = []
    # основной список позиций активный
    instrument_list_active = []
    # заработал ли поток получения ордеров
    socket_work = False



