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

    def get_delta(self, first_balance: float, exchange_rates: float):
        try:
            xxx = float(self.first_val['bid_0']) - 5* float(self.first_symbol_rule['minPrice'])

            qt1 = float(first_balance / xxx)
            qt2 = 0.0
            if self.first_symbol_rule['baseAss'] == self.second_symbol_rule['quoteAss']:
                qt2 = qt1 / self.second_val['ask_0']
            elif self.first_symbol_rule['baseAss'] == self.second_symbol_rule['baseAss']:
                qt2 = qt1 * self.second_val['bid_0']

            yyy =  float(self.third_val['ask_0']) +5* float(self.third_symbol_rule['minPrice'])
            qt3 = qt2 * yyy
            delta = qt3 - first_balance


            self.delta = delta * exchange_rates

            self.min_event_time = sorted([self.first_val['event_time'],
                                          self.second_val['event_time'],
                                          self.third_val['event_time']])[0]
        except Exception as ex:
            self.delta = 0.0
