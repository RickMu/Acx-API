
import sys

sys.path.append("C:\\Users\\Rick\\PycharmProjects\\Acx-API")
print(sys.path)
import logging



from pymongo import MongoClient
import urllib.request
import urllib.error
import json
import threading
import time
import socket
from repository.acx_repo import *
import datetime
from builder_clients.api_clients import *


API = 'https://acx.io:443//api/v2/'
logging.basicConfig(filename='./fetch.log', level=logging.DEBUG)

class Service:
    Tickers = "Tickers"
    Trade = "Trade"
    Depth = "Depth"
    SystemTime = "systime"



class DataFetcherThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.conn = MongoClient('localhost', 27017)

        self.clients =[
            #AcxApiClient(),
            GDXApiClient()
        ]
        self.tickers = {
            self.clients[0]:[],
            #self.clients[1]:[]
        }
        self.cryptoLastID = {
            self.clients[0]: {},
            #self.clients[1]: {}
        }
        self.dbs ={
            #self.clients[0]: AcxDB(),
            self.clients[0]: GdxDB()
        }

    def initialise(self):
        for c in self.clients:
            tickers = c.fetchTickers()
            for t in tickers:
                self.tickers[c].append(t)
        print(self.tickers)

        self.findLastIDs()

    def fetchMarkets(self):
        print("Fetching...")
        self.markets = self.dataFetcher.fetchMarkets()
        print("Fetched all markets")
        for m in self.markets:
            self.cryptoLastID[m] = None


    def findLastIDs(self):
        for c in self.clients:
            for t in self.tickers[c]:
                if t in self.dbs[c].getRepo.keys():
                    repo, error = self.dbs[c].getRepository(t)

                    if(error is not None):
                        raise Exception(error.getErrorMsg())

                    cursor = repo.findLastTrade()
                    i = next(cursor, None)
                    if( i is not None):
                        self.cryptoLastID[c][t] = i['id']
                    else:
                        self.cryptoLastID[c][t] = None



    def insertData(self, client, trades, market):
        print("Inserting data for market: " + market)
        logging.info("Inserting data for market: " + market)

        if (market in self.dbs[client].getRepo.keys()):
            self.cryptoLastID[client][market] = trades[0]['id']
            repo ,error = self.dbs[client].getRepository(market)
            if( error is not None):
                raise Exception(error.getErrorMsg())


            repo.insert(trades)

    def processData(self,data):
        for elem in data:
            if elem['created_at'][-1] == "Z":
                string = elem['created_at'][:-4]

                format = '%Y-%m-%dT%H:%M'
                d = datetime.datetime.strptime(string, format) + datetime.timedelta(hours=11)
                d = d.isoformat() + "+11:00"
                elem['created_at'] = d
        return data

    def run(self):
        while True:
            for c in self.clients:
                for t in self.tickers[c]:
                    time.sleep(5)
                    print("Fetching for Market: "+ t)

                    if t not in self.cryptoLastID[c].keys():
                        continue

                    if self.cryptoLastID[c][t] is not None:
                        trades = c.fetchTrades(t,self.cryptoLastID[c][t])
                    else:
                        trades = c.startFetchTrades(t,100)

                    if (trades is None or len(trades) == 0):
                        print("No trades for Market: "+ t)
                        continue
                    #self.newData.emit(trades, i)
                    print("inserting data...")
                    #self.processData(trades)
                    self.insertData(c, trades,t)




if __name__ == '__main__':




    fetcher = DataFetcherThread()
    fetcher.initialise()
    fetcher.start()
    #data = [{"id": 5660294, "price": "21700.0", "volume": "0.005", "funds": "108.5", "market": "btcaud",
    # "created_at": "2018-01-06T00:28:50Z", "trend": "up", "side": 'null'}]

    #fetcher.processData(data)
    #print(data)


