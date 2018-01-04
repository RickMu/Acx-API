
import datetime as dt
from collections import defaultdict
import pandas as pd

class Coin:
    def __init__(self, coin ):
        self.coin = coin
        self.trades = defaultdict(list)
        self.recentTrades = defaultdict(list)
        self.candleStickData = defaultdict(list)
        self.newTrades = False

    def hasNewTrades(self):
        return self.newTrades

    def addTrades(self, trades):
        trades = list(trades)

        if (trades is None):
            print("Trade is None")
            self.newTrades = False
        elif (len(trades) == 0):
            print('no trades')
            self.newTrades = False
        else:
            self.recentTrades.clear()
            self.recentTrades = defaultdict(list)

            for trade in trades:
                self.addTrade(trade)
            for k in self.recentTrades.keys():
                self.trades[k] = self.recentTrades[k] + self.trades[k]

            self.newTrades = True

    def addTrade(self, trade):
        TRADES_TIME_FORMAT = "%Y-%m-%dT%H:%M"

        timestr = trade['created_at']
        timestr = timestr[:16]
        print(trade['created_at'])
        struct_time = dt.datetime.strptime(timestr, TRADES_TIME_FORMAT)

        if (trade['created_at'][-1] == "Z"):
            # print(trade['created_at'])
            struct_time = struct_time + dt.timedelta(hours=11)
        timestr = struct_time.strftime(TRADES_TIME_FORMAT)
        print(timestr)
        # struct_time = time.strptime(timestr, TRADES_TIME_FORMAT)

        self.recentTrades['time'].append(timestr)
        self.recentTrades['price'].append(float(trade['price']))
        self.recentTrades['id'].append(trade['id'])

        vol = float(trade['volume'])
        cash = (vol * float(trade['price']))

        self.recentTrades['volume'].append(vol)
        self.recentTrades['cash'].append(cash)

    def getLastTradeID(self):
        return self.recentTrades['id'][0]

    def isTradeRecordEmpty(self):
        return len(self.trades['id']) == 0

    def getAllTradesDF(self):
        return pd.DataFrame(self.trades).sort_values(['time'])

    def getRecentTradesDF(self):
        return pd.DataFrame(self.recentTrades)
