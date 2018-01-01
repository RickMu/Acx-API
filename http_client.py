
import pyqtgraph as pg
from Repository import AcxDB
from collections import defaultdict
from http_server import ServerRequest
from http_server import ServerInfo
import urllib
import json


def loadJSON(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
           data = json.load(response)
        return data
    except urllib.error.URLError as error:
        print(error)
        return None

class HttpClient(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object,str)
    def __init__(self, Acx):
        super().__init__()
        self.markets= defaultdict(str)
        self.requestBuilder = ServerRequest(ServerInfo.PORT_NUMBER)
        self.acx = Acx

    def addMarket(self,market):
        self.markets[market] = 1
    def run(self):
        for k in self.markets:
            request = self.requestBuilder.buildAfterTimeRequest(k, day=1)
            data = loadJSON(request)
            m = self.acx.getMarket(k)
            m.addTrades(data)
            trades = m.getAllTradesDF()
            self.newData.emit(trades, k)


if __name__=="__main__":
    requestBuilder = ServerRequest(ServerInfo.PORT_NUMBER)
    request = requestBuilder.buildAfterTimeRequest("btcaud",day=1)
    print(request)

    data = loadJSON(request)
