
from client_server.http_server import *


db =GdxExchange()
requestBuilder = ServerRequest()
ticker = GdxExchange.Ticker.BITCOIN

request = requestBuilder.buildAfterTimeRequest(db,ticker, day=3, hour=0)
#request = self.requestBuilder.buildFindInBetweenRequest(k,2018,1,17,1)
print(request)
data = loadJSON(request)
m = db.coins[ticker]
m.addTrades(data)
trades = m.getAllTradesDF()
trades.to_csv("./3dayCoinBase.csv")