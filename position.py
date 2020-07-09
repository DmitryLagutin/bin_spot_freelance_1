from instrument_tree import *
from settings import *
from binance.enums import *
from trade_helper import *


class Position:
    def __init__(self, instrument_id: str):
        self.id = instrument_id

    def main_func_position(self):
        # делаем пересчет по позиции на актуальные данные
        instrument = [x for x in Main.tree_inst_list if x.id == self.id][0]
        __instrument = instrument
        __first_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.first][0]
        __second_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.second][0]
        __third_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.third][0]

        # если не было не одной сделки, мы начинаем выполнять первую
        if len(Main.trade_level) == 0:
            Main.qt1 = buy_test(symbol=__instrument.first, price=__instrument.first_val['last_price'],
                                qty=100.00)
            Main.trade_level.append(1)
        # вторая сделка, при условии, что была первая
        elif len(Main.trade_level) == 1:
            if __first_symbol_rule['baseAss'] == __second_symbol_rule['quoteAss']:
                Main.qt2 = buy_test(symbol=__instrument.second, price=__instrument.second_val['last_price'],
                                    qty=Main.qt1)
                Main.trade_level.append(1)
            # -----------------!!!!!!!!
            elif __first_symbol_rule['baseAss'] == __second_symbol_rule['baseAss']:
                Main.qt2 = sell_test(symbol=__instrument.second, price=__instrument.second_val['last_price'],
                                     qty=Main.qt1)
                Main.trade_level.append(1)
        # третья сделка, при условии, что была первая и вторая
        elif len(Main.trade_level) == 2:
            Main.qt3 = sell_test(symbol=__instrument.third, price=__instrument.third_val['last_price'],
                                 qty=Main.qt2)
            Main.trade_level.append(1)

        # если все сделки были сделаны, то удаляем позицию и обнуляем данные трейдов
        if len(Main.trade_level) == 3:
            print(Main.trade_level, Main.qt3)
            print("Удалена позиция")
            Main.trade_level = []
            Main.qt1 = 0.0
            Main.qt2 = 0.0
            Main.qt3 = 0.0

            Main.position = None
