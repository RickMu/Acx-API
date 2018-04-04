
from visual_tool.client_server.http_client import SmartRequests
from visual_tool.exchange.exchange import *


db =GdxExchange()
ticker = GdxExchange.Ticker.BITCOIN

smartRequest = SmartRequests()
smartRequest.set(db, ticker, day=20, hour=0)

#request = self.requestBuilder.buildFindInBetweenRequest(k,2018,1,17,1)
trades, suppTrades = smartRequest.buildAfterTimeRequest()
trades.to_csv("./12dayCoinBase.csv")


