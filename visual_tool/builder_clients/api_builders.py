

class GDXApiBuilder:
    API = "https://api.gdax.com"


    class Service:
        TRADES = "trades"



    def __init__(self):
        self.api = GDXApiBuilder.API

    def clear(self):
        self.api = GDXApiBuilder.API
        return self

    def getAPI(self):
        api = self.api
        self.clear()
        return api

    def products(self):
        self.api+="/products"
        return self

    def currency(self,ticker):
        self.api += "/products/"+ticker
        return self

    def limit(self,lim):
        self.api +="limit="+str(lim)
        return self

    def service(self,service):
        self.api += "/"+service
        return self

    def PARAMS(self):
        self.api+= "?"
        return self

    def before(self, id):
        self.api += "before=" +str(id)
        return self


    def after(self, id):
        self.api += "after=" +str(id)
        return self










class PoloniexApiBuilder:
    API = "https://poloniex.com/public?command="
    class Service:
        returnTradeHistory = "returnTradeHistory"


    def __init__(self):
        self.api = PoloniexApiBuilder.API

    def clear(self):
        self.api = PoloniexApiBuilder.API
        return self
    def getAPI(self):
        api = self.api
        self.clear()
        return api

    def service(self,service):
        self.api+=service
        return self
    def AND(self):
        self.api += "&"
        return self

    def currency(self, coin):
        self.api+=("currencyPair="+coin)
        return self

    def startTime(self,time):
        self.api+=("start="+str(time))
        return self

    def endTime(self,time):
        self.api+=("end="+str(time))
        return self

    def returnTradeHistoryApi(self,coin,start,end):
        self.service(PoloniexApiBuilder.Service.returnTradeHistory)\
            .AND().currency(coin).AND().startTime(start).AND().endTime(end)
        api = self.getAPI()
        return api




class AcxApiBuilder:
    API = 'https://acx.io:443//api/v2/'
    class Service:
        Tickers = "Tickers"
        Trade = "Trade"
        Depth = "Depth"
        SystemTime = "systime"


    def __init__(self):
        self.api = AcxApiBuilder.API

    def getAPI(self):

        api = self.api
        self.clear()
        return api

    def service(self, service):

        if (service == AcxApiBuilder.Service.Tickers):
            self.api = self.api + "tickers.json"
        elif (service == AcxApiBuilder.Service.Trade):
            self.api = self.api + "trades.json"

        elif (service == AcxApiBuilder.Service.Depth):
            self.api = self.api + "depth.json"
        elif (service == AcxApiBuilder.Service.SystemTime):
            self.api = self.api + "timestamp.json"
        return self

    def market(self, market):
        self.api = self.api + "?market=" + market
        return self

    def fromID(self, id):
        self.api = self.api + "from=" + str(id)

        return self

    def AND(self):
        self.api += "&"
        return self

    def limit(self, limit):
        self.api += ("limit=" + str(limit))

        return self

    def clear(self):
        self.api = AcxApiBuilder.API
        return self


if __name__ == "__main__":
    import json
    polo = PoloniexApiBuilder()
    api = polo.returnTradeHistoryApi("BTC_NXT",111123,333133)

    gdxApi = GDXApiBuilder()

    api = gdxApi.currency("BTC-USD").service(GDXApiBuilder.Service.TRADES).PARAMS().before(34715243).getAPI()


    print(api)
