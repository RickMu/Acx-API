import json
import urllib
from collections import defaultdict

import pyqtgraph as pg

from client_server.http_server import ServerInfo
from client_server.http_server import ServerRequest


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
    def __init__(self, Acx):
        super().__init__()
        self.market = None
        self.requestBuilder = ServerRequest(ServerInfo.PORT_NUMBER)
        self.acx = Acx
    def setMarket(self,market):
        self.market = market


    def run(self):
        if self.market == None:
            raise Exception("Market cannot be none")

        k = self.market
        request = self.requestBuilder.buildAfterTimeRequest(k, day=2,hour=0)
        data = loadJSON(request)
        m = self.acx.coins[k]
        m.addTrades(data)
        trades = m.getAllTradesDF()
        self.newData.emit(trades, k)


if __name__=="__main__":

    '''
    Qt Thread only works when theres qt objects around

    '''
    requestBuilder = ServerRequest(ServerInfo.PORT_NUMBER)
    request = requestBuilder.buildAfterTimeRequest("btcaud",day=1)

    def test(data, market):
        print(data)
        print(market)
    from exchange.acx_exchange import AcxExchange
    acx =AcxExchange()
    client = HttpClient(acx)
    client.addMarket(AcxExchange.Market.BITCOIN)
    client.newData.connect(test)
    client.start()




