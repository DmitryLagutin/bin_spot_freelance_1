from binance.client import Client


class Main:
    # клиент
    client = Client('QGW0R9hOCKQyqcx8TWL2ugrE3giEntsxhAcEBa6PPhlvW1JthyTZDuaZ4ucn19Uk',
                    'IRPUlOIuiPvcnxTxeb4FzztBMGu88il7avCT3kyHzztfrzSqq4e2x6pQT6e3f3hD')
    # правила биржи
    exchange_rules = []
    # список троек
    tree_list = []
    # список свободных балансов
    balance_list = []

    # основной список инструментов активный
    instrument_list = []
    # список основных троек cписок объектов
    tree_inst_list = []

    # основная тройка иструментов
    main_tree_object = None

    # основная позиция
    position = None

    trade_level = []


    qt1 = 0.0
    qt2 = 0.0
    qt3 = 0.0

