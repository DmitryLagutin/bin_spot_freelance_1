from settings import *
from trade_helper import *
import enum


class InstrumentTree:

    def __init__(self, first, first_val, second, second_val, third, third_val):
        self.id = first + second + third
        self.first = first
        self.first_val = first_val
        self.second = second
        self.second_val = second_val
        self.third = third
        self.third_val = third_val

        self.first_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == first][0]
        self.second_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == second][0]
        self.third_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == third][0]

    def min_qty(self, ticker):
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

    def get_delta(self, first_balance: float, exchange_rates: float):
        try:
            xxx = float(self.first_val['bid_0']) - 0 * float(self.first_symbol_rule['minPrice'])

            qt1 = float("{:0.0{}f}".format(first_balance / xxx, self.min_qty(self.first)))
            qt2 = 0.0
            if self.first_symbol_rule['baseAss'] == self.second_symbol_rule['quoteAss']:
                qt2 = float("{:0.0{}f}".format(qt1 / self.second_val['bid_0'], self.min_qty(self.second)))
            elif self.first_symbol_rule['baseAss'] == self.second_symbol_rule['baseAss']:
                qt2 = float("{:0.0{}f}".format(qt1 * self.second_val['ask_0'], self.min_qty(self.second)))
            yyy = float(self.third_val['ask_0']) + 0 * float(self.third_symbol_rule['minPrice'])
            qt3 = float("{:0.0{}f}".format(qt2 * yyy, self.min_qty(self.third)))
            delta = qt3 - first_balance

            comission = (first_balance * 0.075 / 100) * 3
            self.delta = (delta - comission) * exchange_rates

            self.min_event_time = sorted([self.first_val['event_time'],
                                          self.second_val['event_time'],
                                          self.third_val['event_time']])[0]

            self.num_of_trades = sorted([self.first_val['num_of_trades'],
                                         self.second_val['num_of_trades'],
                                         self.third_val['num_of_trades']])[0] / (24 * 3600)

        except Exception as ex:
            print(str(ex))
            self.delta = 0.0
