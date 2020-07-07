from settings import *
from trade_helper import *
import enum


class LevelTrade(enum.Enum):
    first_trade = 0
    second_trade = 1
    third_trade = 2


class Instrument:

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
        self.thrid_symbol_rule = [x for x in Main.exchange_rules if x['ticker'] == third][0]

    def get_delta(self, first_balance: float, exchange_rates: float):
        try:
            first = self.first_val['last_price']
            second = self.second_val['last_price']
            thrid = self.third_val['last_price']

            qt1 = first_balance / first
            qt2 = 0.0
            if self.first_symbol_rule['baseAss'] == self.second_symbol_rule['quoteAss']:
                qt2 = qt1 / second
            elif self.first_symbol_rule['baseAss'] == self.second_symbol_rule['baseAss']:
                qt2 = qt1 * second
            qt3 = qt2 * thrid
            delta = qt3 - first_balance
            self.delta = delta * exchange_rates
        except Exception as ex:
            self.delta = 0.0

