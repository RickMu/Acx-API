from pymongo import MongoClient
import urllib.request
import urllib.error
import json
import threading
import time
import socket
from builders.acx_builder import AcxApiBuilder
from exchange.acx_exchange import AcxExchange
from repository.acx_repo import AcxDB



API = 'https://acx.io:443//api/v2/'

class Service:
    Tickers = "Tickers"
    Trade = "Trade"
    Depth = "Depth"
    SystemTime = "systime"


class AcxDataFetcher():

    def __init__(self):
        self.apiBuilder  = AcxApiBuilder()

    def loadJSON(self,url):
        try:
            response = urllib.request.urlopen(url,timeout=5)
            data = json.load(response)
            return data
        except socket.timeout as timeout:
            print("timed out...")
            print(timeout)
            return None
        except urllib.error.HTTPError as error:
            print(error)
            return None
        except urllib.error.URLError as error:
            print(error)
            return None


    def fetchMarkets(self):
        tickersUrl = self.apiBuilder.service(Service.Tickers).getAPI()
        tickers = self.loadJSON(tickersUrl)

        print(tickers)
        markets= {}
        for market in tickers:
            markets[market]=1

        print(markets)
        return markets

    def fetchTrades(self, limit, market, lastTradeID = None):
        # Later I think should limit by using DateTime rather then limit

        if (lastTradeID is None):
            tradesUrl = self.apiBuilder.service(Service.Trade).market(market).AND().limit(limit).getAPI()
        else:
            tradesUrl = self.apiBuilder.service(Service.Trade).market(market).AND().fromID(lastTradeID).getAPI()
        print(tradesUrl)
        trades = self.loadJSON(tradesUrl)
        return trades



class DataFetcherThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.conn = MongoClient('localhost', 27017)
        self.dataFetcher = AcxDataFetcher()
        self.markets = {}
        self.cryptoLastID = {}
        self.db =AcxDB()
    def initialise(self):
        self.fetchMarkets()
        self.findLastIDs()

    def fetchMarkets(self):
        print("Fetching...")
        self.markets = self.dataFetcher.fetchMarkets()
        print("Fetched all markets")
        for m in self.markets:
            self.cryptoLastID[m] = None


    def findLastIDs(self):
        for market in self.markets.keys():
            if market in self.db.getRepo.keys():
                repo, error = self.db.getRepository(market)

                if(error is not None):
                    raise Exception(error.getErrorMsg())

                cursor = repo.findLastTrade()
                i = next(cursor, None)
                if( i is not None):
                    self.cryptoLastID[market] = i['id']

    def insertData(self, trades, market):
        print("Inserting data for market: " + market)
        if (market in self.db.getRepo.keys()):
            self.cryptoLastID[market] = trades[0]['id']
            repo ,error = self.db.getRepository(market)
            if( error is not None):
                raise Exception(error.getErrorMsg())

            repo.insert(trades)

    def run(self):
        while True:
            for i in self.markets:
                print("Fetching for Market: "+ i)
                trades = self.dataFetcher.fetchTrades(100, i, lastTradeID=self.cryptoLastID[i])
                if (trades is None or len(trades) == 0):
                    print("No trades for Market: "+ i)
                    continue
                #self.newData.emit(trades, i)
                print("inserting data...")
                self.insertData(trades,i)
                time.sleep(12)




if __name__ == '__main__':
    fetcher = DataFetcherThread()
    fetcher.initialise()
    fetcher.start()

    import signal
    signal.signal(signal.SIGALRM)
