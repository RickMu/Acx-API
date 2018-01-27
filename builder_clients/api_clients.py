import abc
from builder_clients.api_builders import *
import urllib.error
import urllib.request
import socket
import json
import datetime

'''
Need a unified format for json data from every exchange
if some are missing input null

Trades
{
    created_at: "2018-01-26T10:25:58.96Z",
    id: 34714958,
    price: "10473.51000000",
    volume: "0.06000000",
    side: "sell"
    trend: "down",
},


'''

class UnifiedFormat:
    @abc.abstractmethod
    def __unifyTradesFormat(self,tradeJson):
        return

    @abc.abstractmethod
    def __unifyTimeFormat(self,time_str):
        return


class client:
    def loadJSON(self,url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
            }

            #handler = urllib.request.ProxyHandler({"http":'79.137.42.124:3128'})
            #opener = urllib.request.build_opener(handler)
            #urllib.request.install_opener(opener)
            #req = urllib.request.Request(url,headers= headers)
            response = urllib.request.urlopen(url,timeout=5)
            response = response.read().decode('utf-8')
            data = json.loads(response)
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
    @abc.abstractmethod
    def fetchTickers(self):
        return

    @abc.abstractmethod
    def fetchTrades(self, ticker, lastTradeID):
        return

    @abc.abstractmethod
    def startFetchTrades(self,ticker, limit):
        return




class AcxApiClient(client,UnifiedFormat):

    def __init__(self):
        self.apiBuilder  = AcxApiBuilder()

    def fetchTickers(self):
        '''

        :return:
        markets ={
            btc-aud:1
            ....
        }
        '''

        tickersUrl = self.apiBuilder.service(AcxApiBuilder.Service.Tickers).getAPI()
        tickers = self.loadJSON(tickersUrl)
        markets= {}
        for market in tickers:
            markets[market]=1
        return markets

    def fetchTrades(self,ticker, lastTradeID):

        '''
        API = https://acx.io:443//api/v2/trades.json?market=btcaud&limit=100

        JSON
        {
            {
            id: 6893069,
            price: "13455.0",
            volume: "0.0884",
            funds: "1189.422",
            market: "btcaud",
            created_at: "2018-01-26T22:16:29+11:00",
            trend: "down",
            side: null
            },
            ....
        }
        '''

        tradesUrl = self.apiBuilder.service(AcxApiBuilder.Service.Trade).market(ticker).AND().fromID(lastTradeID).getAPI()
        print(tradesUrl)

        trades = self.loadJSON(tradesUrl)

        trades= self.__unifyTradesFormat(trades)

        return trades

    def startFetchTrades(self, ticker, limit):
        tradesUrl = self.apiBuilder.service(AcxApiBuilder.Service.Trade).market(ticker).AND().limit(limit).getAPI()

        trades = self.loadJSON(tradesUrl)
        trades= self.__unifyTradesFormat(trades)

        return trades

    def __unifyTradesFormat(self,tradeJson):
        '''{
            created_at: "2018-01-26T10:25:58.96Z",
            id: 34714958,
            price: "10473.51000000",
            volume: "0.06000000",
            side: "sell"
            trend: "down",
        },

            {
            id: 6893069,
            price: "13455.0",
            volume: "0.0884",
            created_at: "2018-01-26T22:16:29+11:00",
            trend: "down",
            side: null
                funds: "1189.422",
                market: "btcaud",
            },
        '''
        for t in tradeJson:
            del t['funds']
            del t['market']

            t['created_at'] = self.__unifyTimeFormat(t['created_at'])

        return tradeJson

    def __unifyTimeFormat(self,time_str):

        if time_str[-1] == "Z":
            time_str = time_str[:-4]

            format = '%Y-%m-%dT%H:%M'
            d = datetime.datetime.strptime(time_str, format) + datetime.timedelta(hours=11)
            d = d.isoformat() + "+11:00"
            time_str = d
        return time_str








class GDXApiClient(client,UnifiedFormat):

    def __init__(self):
        self.apiBuilder  = GDXApiBuilder()

    def fetchTickers(self):
        '''
        API https://api.gdax.com//products

        Only want BCH-USD
        JSON:
        {
                {
                    id: "BCH-USD",  T
                    base_currency: "BCH",
                    quote_currency: "USD",
                    base_min_size: "0.01",
                    base_max_size: "350",
                    quote_increment: "0.01",
                    display_name: "BCH/USD",
                    status: "online",
                    margin_enabled: false,
                    status_message: null,
                    min_market_funds: "10",
                    max_market_funds: "1000000",
                    post_only: false,
                    limit_only: false,
                    cancel_only: false
                }
        }

            :return:
            markets ={
                btc-usd:1
                ....
        }
        '''

        tickerData = self.__getTickers()
        tickers = {}

        for d in tickerData:

            if 'USD' in d['id']:
                tickers[d['id']]=1

        return tickers

    def fetchTrades(self,ticker, lastTradeID = None):
        # Later I think should limit by using DateTime rather then limit
        '''

        api = "https://api.gdax.com/products/BTC-USD/trades?before=lastTradeID"
        JSON :
        {
            {
                time: "2018-01-26T10:25:58.96Z",
                trade_id: 34714958,
                price: "10473.51000000",
                size: "0.06000000",
                side: "sell"
            },
            ......
        }
        '''


        trades = self.__getTradesBeforeID(ticker, lastTradeID)
        trades = self.__unifyTradesFormat(trades)

        return trades

    def startFetchTrades(self, ticker, limit):
        '''
        Format same as before

        used only when database has no data of this ticker
        '''
        trades = self.__getTradesGivenLimit(ticker,limit)
        trades = self.__unifyTradesFormat(trades)
        return trades

    def __getTradesGivenLimit(self,ticker, limit):
        api = self.apiBuilder.currency(ticker).service(GDXApiBuilder.Service.TRADES) \
            .PARAMS().limit(limit).getAPI()

        print(api)
        trades = self.loadJSON(api)
        return trades

    def __getTradesBeforeID(self,ticker,id):
        api = self.apiBuilder.currency(ticker).service(GDXApiBuilder.Service.TRADES) \
        .PARAMS().before(id).getAPI()

        print(api)

        trades = self.loadJSON(api)


        return trades

    def __getTickers(self):
        api = self.apiBuilder.products().getAPI()
        tickers = self.loadJSON(api)
        return tickers

    def __unifyTradesFormat(self,tradeJson):
        '''

        {
            created_at: "2018-01-26T10:25:58.96Z",
            id: 34714958,
            price: "10473.51000000",
            volume: "0.06000000",
            side: "sell"
            trend: "down",
        },


        Returned
        {
            {
                time: "2018-01-26T10:25:58.96Z",
                trade_id: 34714958,
                price: "10473.51000000",
                size: "0.06000000",
                side: "sell"
            },
            ......
        }
        '''

        for t in tradeJson:
            t['created_at']= self.__unifyTimeFormat(t['time'])
            del t['time']
            t['id']= t['trade_id']
            del t['trade_id']
            t['volume'] = t['size']
            del t['size']
            t['trend']= None

        return tradeJson


    def __unifyTimeFormat(self,time_str):
        "2018-01-27T04: 29:39.035Z"
        #count to the second :
        if time_str[-1] == "Z":
            for i in range(len(time_str)-1,0,-1):
                if time_str[i]==":":
                    time_str = time_str[:i]
                    format = '%Y-%m-%dT%H:%M'
                    d = datetime.datetime.strptime(time_str, format) + datetime.timedelta(hours=11)
                    d = d.isoformat() + "+11:00"
                    time_str = d
                    break
        return time_str





if __name__ == "__main__":
    #apiClient = AcxApiClient()
    #trades = apiClient.startFetchTrades('btcaud', 100)

    apiClient = GDXApiClient()
    trades = apiClient.fetchTickers()
    print(trades)
