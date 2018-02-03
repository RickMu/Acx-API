import json
import urllib
from collections import defaultdict

import pyqtgraph as pg

from visual_tool.client_server.http_server import ServerInfo
from visual_tool.client_server.http_server import ServerRequest


def loadJSON(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
           data = json.load(response)
        return data
    except urllib.error.URLError as error:
        print(error)
        return None

class HttpClient(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object,str)
    def __init__(self, db):
        super().__init__()
        self.market = None
        self.requestBuilder = ServerRequest()
        self.db = db
    def setMarket(self,market):
        self.market = market


    def run(self):
        if self.market == None:
            raise Exception("Market cannot be none")

        k = self.market
        request = self.requestBuilder.buildAfterTimeRequest(self.db,k, day=2, hour=0)
        #request = self.requestBuilder.buildFindInBetweenRequest(k,2018,1,17,1)
        print(request)
        data = loadJSON(request)
        m = self.db.coins[k]
        m.addTrades(data)
        trades = m.getAllTradesDF()
        self.newData.emit(trades, k)


if __name__=="__main__":

    '''
    Qt Thread only works when theres qt objects around

    '''

    def test(data, market):
        print(data)
    from visual_tool.exchange.exchange import*
    db =GdxExchange()
    client = HttpClient(db)
    client.newData.connect(test)
    client.start()



