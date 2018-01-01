

API = 'https://acx.io:443//api/v2/'
class Service:
    Tickers = "Tickers"
    Trade = "Trade"
    Depth = "Depth"
    SystemTime = "systime"


class AcxApiBuilder:
    def __init__(self):
        self.api = API

    def getAPI(self):

        api = self.api
        self.clear()
        return api

    def service(self, service):

        if (service == Service.Tickers):
            self.api = self.api + "tickers.json"
        elif (service == Service.Trade):
            self.api = self.api + "trades.json"

        elif (service == Service.Depth):
            self.api = self.api + "depth.json"
        elif (service == Service.SystemTime):
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
        self.api = API
        return self