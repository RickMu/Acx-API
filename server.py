from pymongo import MongoClient
import pymongo
from abc import abstractmethod
import urllib.request
import json
import threading
import time

API = 'https://acx.io:443//api/v2/'

class Service:
    Tickers = "Tickers"
    Trade = "Trade"
    Depth = "Depth"
    SystemTime = "systime"




def insert( collection, instance):
    try:
        collection.insert(instance)
    except pymongo.errors.DuplicateKeyError as error:
        print(error)


def findAll( collection):
    return collection.find()
def clear(collection):
    collection.remove()

def findMax( collection, column):
    return sort(collection, column, limit=1)


def findMin( collection, column):
    return sort(collection, column, ascending=False, limit=1)


def sort( collection, column, largestFirst=True, limit=None):
    order = -1
    if (largestFirst == False):
        order = 1
    if (limit is not None):
        return collection.find().sort([(column, order)]).limit(limit)

    return collection.find().sort([(column, 1)])




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


class Repository():
    @abstractmethod
    def insert(self, instance):
        return

    @abstractmethod
    def findAll(self):
        return
    @abstractmethod
    def clear(self):
        return

class MongoRepo(Repository):
    BITCOIN = "btcaud"
    ETHER = "ethaud"
    HSR = "hsraud"
    BCH = "bchaud"
    def __init__(self, type, conn):

        self.db = conn.Acx
        if(type == MongoRepo.BITCOIN):
            self.cryptocoin = self.db.bitcoin
        elif(type== MongoRepo.ETHER):
            self.cryptocoin = self.db.ether
        elif(type== MongoRepo.HSR):
            self.cryptocoin = self.db.hsr
        elif(type== MongoRepo.BCH):
            self.cryptocoin = self.db.bch

    def insert(self, instance):
        super().insert(instance)
        insert(self.cryptocoin, instance)

    def findAll(self):
        return findAll(self.cryptocoin)

    def findLastTrade(self):
        return findMax(self.cryptocoin, "id")

    def clear(self):
        super().clear()
        self.cryptocoin.remove()



class AcxDataFetcher():

    def __init__(self):
        self.apiBuilder  = AcxApiBuilder()

    def loadJSON(self,url):
        try:
            response = urllib.request.urlopen(url,timeout=5)
            data = json.load(response)
            return data
        except urllib.error.HTTPError as error:
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
        self.cryptoCoinRepo = {
            MongoRepo.BITCOIN: MongoRepo(MongoRepo.BITCOIN, self.conn),
            MongoRepo.ETHER: MongoRepo(MongoRepo.ETHER, self.conn),
            MongoRepo.HSR: MongoRepo(MongoRepo.HSR, self.conn),
            MongoRepo.BCH: MongoRepo(MongoRepo.BCH, self.conn)
        }
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
            if market in self.cryptoCoinRepo:
                repo = self.cryptoCoinRepo[market]
                i = next(repo.findLastTrade(), None)
                if( i is not None):
                    self.cryptoLastID[market] = i['id']

    def insertData(self, trades, market):
        print("Inserting data for market: " + market)
        if (market in self.cryptoCoinRepo):
            self.cryptoLastID[market] = trades[0]['id']
            self.cryptoCoinRepo[market].insert(trades)

    def run(self):
        while True:
            for i in self.cryptoCoinRepo:
                print("Fetching for Market: "+ i)
                trades = self.dataFetcher.fetchTrades(100, i, lastTradeID=self.cryptoLastID[i])
                if (trades is None or len(trades) == 0):
                    continue
                #self.newData.emit(trades, i)
                print("inserting data")
                self.insertData(trades,i)
                time.sleep(12)







fetcher = DataFetcherThread()
fetcher.initialise()
fetcher.start()












'''

#查询全部
for i in my_set.find():
    print(i)
#查询name=zhangsan的
for i in my_set.find({"name":"zhangsan"}):
    print(i)
print(my_set.find_one({"name":"zhangsan"}))
'''
'''

#删除name=lisi的全部记录
my_set.remove({'name': 'zhangsan'})

#删除name=lisi的某个id的记录
id = my_set.find_one({"name":"zhangsan"})["_id"]
my_set.remove(id)

#删除集合里的所有记录
db.users.remove()　

'''
