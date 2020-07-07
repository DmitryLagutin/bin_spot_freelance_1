from instrument import *
from settings import *
from binance.enums import *
from trade_helper import *


class Position:

    def make_fields(self):
        """
        Функция, присваивает значения полям
        """
        instrument = [x for x in Main.tree_inst_list if x.id == self.id][0]
        self.instrument = instrument
        self.first = instrument.first
        self.first_val = instrument.first_val
        self.second = instrument.second
        self.second_val = instrument.second_val
        self.third = instrument.third
        self.third_val = instrument.third_val
        self.first_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.first][0]
        self.second_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.second][0]
        self.thrid_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == instrument.third][0]

    def __init__(self, instrument_id: str):
        """
        Функция, которая создает экземпляр класса
        """
        self.id = instrument_id
        self.make_fields()

    def __replay__(self):
        """
        Приватная функция, которая делает перерасчет позиции
        """
        self.make_fields()

    def buy_order(self, symbol, qty):
        try:
            order = Main.client.create_order(
                symbol=symbol,
                side="BUY",
                type=ORDER_TYPE_MARKET,
                quantity=qty)

            print(order['symbol'], order['origQty'], order['fills'][0]['price'])


        except Exception as ex:
            return str(ex)

    def sell_order(self, symbol, qty):
        try:
            order = Main.client.create_order(
                symbol=symbol,
                side="SELL",
                type=ORDER_TYPE_MARKET,
                quantity=qty)
            print(order['symbol'], order['origQty'], order['fills'][0]['price'])

        except Exception as ex:
            return str(ex)

    def buy_test(self, symbol, price, qty):
        qty_x = qty / price
        print(symbol, 'BUY---', get_qty_for_trade(qty_x, min_qty(symbol)), min_qty(symbol))
        return qty_x

    def sell_test(self, symbol, price, qty):
        qty_x = qty * price
        print(symbol, 'SELL---', qty_x)
        return qty_x

    def main_func_position(self):
        """
        Основная функция, которая работает с позицией
        """
        # делаем пересчет по позиции на актуальные данные
        self.__replay__()
        # если не было не одной сделки, мы начинаем выполнять первую
        if len(Main.trade_level) == 0:
            Main.qt1 = self.buy_test(symbol=self.first, price=self.first_val['last_price'], qty=100.00)
            Main.trade_level.append(1)
        # вторая сделка, при условии, что была первая
        elif len(Main.trade_level) == 1:
            if self.first_symbol_rule['baseAss'] == self.second_symbol_rule['quoteAss']:
                Main.qt2 = self.buy_test(symbol=self.second, price=self.second_val['last_price'], qty=Main.qt1)
                Main.trade_level.append(1)
            # -----------------!!!!!!!!
            elif self.first_symbol_rule['baseAss'] == self.second_symbol_rule['baseAss']:
                Main.qt2 = self.sell_test(symbol=self.second, price=self.second_val['last_price'], qty=Main.qt1)
                Main.trade_level.append(1)
        # третья сделка, при условии, что была первая и вторая
        elif len(Main.trade_level) == 2:
            Main.qt3 = self.sell_test(symbol=self.third, price=self.third_val['last_price'], qty=Main.qt2)
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
