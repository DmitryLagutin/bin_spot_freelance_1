from binance.client import Client


class Main:
    # клиент
    client = Client('QGW0R9hOCKQyqcx8TWL2ugrE3giEntsxhAcEBa6PPhlvW1JthyTZDuaZ4ucn19Uk',
                    'IRPUlOIuiPvcnxTxeb4FzztBMGu88il7avCT3kyHzztfrzSqq4e2x6pQT6e3f3hD')
    # правила биржи
    exchange_rules = []
    # список троек
    tree_list = []

    # базовый символ
    basic_symbol = 'USDT'
    # базовый баланс
    balance = float(0)
    # список свободных балансов
    balance_list = []
    # основной список позиций активный
    instrument_list = []
    # заработал ли поток получения ордеров
    socket_work = False



