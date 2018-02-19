import json
import urllib
from collections import defaultdict
import datetime

import pyqtgraph as pg

from visual_tool.client_server.http_server import ServerRequest


class SmartRequests:
    def loadJSON(self, url):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.load(response)
            return data
        except urllib.error.URLError as error:
            print(error)
            return None

    def __init__(self):
        self.requestBuilder = ServerRequest()
        self.ticker= None
        self.day=0
        self.hour=0
        self.minute=0
        self.db = None

    def set (self,db, ticker, day, hour, minute=0):
        self.db = db
        self.ticker = ticker
        self.day = day
        self.hour = hour
        self.minute =minute


    def supportData(self,systime):
        #1 day support data

        rq = self.requestBuilder.buildFindInBetweenRequest(self.db, self.ticker, systime.year,
                                                           systime.month, systime.day, systime.hour, systime.minute, 1)

        sup =  self.loadJSON(rq)
        return sup




    def buildAfterTimeRequest(self):
        systime = datetime.datetime.utcnow()+ datetime.timedelta(hours=11)
        requests = []
        for d in range(self.day):
            rq = self.requestBuilder.buildFindInBetweenRequest(self.db,self.ticker,systime.year,
                                                          systime.month,systime.day,systime.hour,systime.minute,1)
            systime = systime - datetime.timedelta(days=1)
            requests.append(rq)
            print(rq)

        if self.hour is not 0:
            rq = self.requestBuilder.buildFindInBetweenRequest(self.db, self.ticker, systime.year,
                                                               systime.month, systime.day,systime.hour,systime.minute, 0,self.hour)
            requests.append(rq)
            systime = systime - datetime.timedelta(hours= self.hour)

        data = []
        for r in requests:
            data +=self.loadJSON(r)

        suppData = self.supportData(systime)


        m = self.db.coins[self.ticker]
        m.addTrades(data)
        trades = m.getAllTradesDF()

        m.addTrades(suppData)
        suppTrades = m.getRecentTradesDF()

        return trades, suppTrades
        #print(requests)












class HttpClient(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object,object)
    def __init__(self, db, ticker):
        super().__init__()
        self.ticker = ticker
        self.smartRequest = SmartRequests()
        self.db = db

    def initialize(self):
        self.smartRequest.set(self.db, self.ticker, day=5, hour=3)

    def run(self):
        if self.ticker == None:
            raise Exception("Market cannot be none")
        self.initialize()
        #request = self.requestBuilder.buildFindInBetweenRequest(k,2018,1,17,1)
        #data = loadJSON(request)

        trades, suppTrades = self.smartRequest.buildAfterTimeRequest()
        self.newData.emit(trades, suppTrades)




if __name__=="__main__":

    '''
    Qt Thread only works when theres qt objects around

    '''
    '''
        def test(data, market):
            print(data)
        from visual_tool.exchange.exchange import*
        db =GdxExchange()
        client = HttpClient(db)
        client.newData.connect(test)
        client.start()
    '''
    from visual_tool.exchange.exchange import*
    db = GdxExchange()
    sq = SmartRequests()

    sq.set(GdxExchange(),GdxExchange.Ticker.ETHER,day=0,hour=3)





    trades = sq.buildAfterTimeRequest()

    print(trades)






