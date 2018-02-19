
import pandas as pd
import time
import datetime as dt






class TimeFormat:
    TRADES_TIME_FORMAT = "%Y-%m-%dT%H:%M"

    def makeTimeIntervals(tradesDF, interval='min',time_interval= 5):

        if tradesDF is None:
            return

        x = tradesDF['time'].values

        x = [dt.datetime.strptime(i, TimeFormat.TRADES_TIME_FORMAT) for i in x]

        if (interval == 'min'):
            for i in range(len(x)):
                c = int(x[i].minute) // time_interval + 1

                x[i] = x[i].replace(minute=(c * time_interval - 1))
        elif (interval == 'hour'):
            for i in range(len(x)):

                c = int(x[i].hour) // time_interval +1
                x[i] = x[i].replace(hour=(c*time_interval - 1))
                x[i] = x[i].replace(minute=(59))

        elif (interval == 'day'):
            for i in range(len(x)):
                c = int(x[i].day) //time_interval + 1

                x[i] = x[i].replace(day=(c*time_interval-1))
                x[i] = x[i].replace(hour=24).replace(minute=59)

        x = [i.strftime( TimeFormat.TRADES_TIME_FORMAT) for i in x]
        tradesDF['interval'] = x

        return tradesDF
def parseSideVolume(tradesDF):

    if ('interval' in tradesDF):
        d = dict((tradesDF.groupby('interval').sum())['side'])

    else:
        d = dict((tradesDF.groupby('time').sum())['side'])
    x = []
    y = []

    for k, v in d.items():
        x.append(k)
        y.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    return x, y


def parseVolume(tradesDF):


    if ('interval' in tradesDF):
        d = dict((tradesDF.groupby('interval').sum())['volume'])

    else:
        d = dict((tradesDF.groupby('time').sum())['volume'])
    x = []
    y = []

    for k, v in d.items():
        x.append(k)
        y.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    return x, y


def datetimeToTimeStamp(d):
    d= [dt.datetime.strptime(i,TimeFormat.TRADES_TIME_FORMAT) for i in d]

    t = [i.timetuple() for i in d]

    timeStamp = [ int(time.mktime(i)) for i in t]
    return timeStamp




def parse(data):
    '''
    if type(data) is not pd.DataFrame:
        raise Exception("Data should be type dataframe")
    '''
    return


def parsePrice(data):

    parse(data)
    if ('interval' in data):
        d = dict((data.groupby('interval').mean())['price'])
    else:
        d = dict((data.groupby('time').mean())['price'])

    x = []
    y = []

    for k, v in d.items():
        x.append(k)
        y.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    return x, y



def parseStdDev( data):
    parse(data)
    if ('interval' in data):
        s = dict((data.groupby('interval').std())['price'])
    else:
        s = dict((data.groupby('time').std())['price'])

    sx = []
    sy = []

    for k, v in s.items():
        sx.append(k)
        sy.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    sx = datetimeToTimeStamp(sx)
    return sx, sy

def parseVolume(data):
    parse(data)

    if ('interval' in data):
        d = dict((data.groupby('interval').sum())['volume'])
    else:
        d = dict((data.groupby('time').sum())['volume'])

    x = []
    y = []
    for k, v in d.items():
        x.append(k)
        y.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    return x, y


def parseVolume(data):
    parse(data)
    if ('interval' in data):
        d = dict((data.groupby('interval').sum())['volume'])
    else:
        d = dict((data.groupby('time').sum())['volume'])

    x = []
    y = []
    for k, v in d.items():
        x.append(k)
        y.append(v)

        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    return x, y



def parse24HrVolume(data):
    parse(data)

    print(len(data['main']))
    print(len(data['support']))

    suppdata = data['support']

    if ('interval' in data['main']):

        sd = dict((suppdata.groupby('interval').sum())['volume'])
        d = dict((data['main'].groupby('interval').sum())['volume'])
    else:
        sd = dict((suppdata.groupby('time').sum())['volume'])
        d = dict((data['main'].groupby('time').sum())['volume'])


    sdk = list(sd.keys())
    sdk.sort()
    dk = list(d.keys())
    dk.sort()

    allk = sdk+dk

    start_volume= 0
    for i in sdk:
        start_volume+=sd[i]

    volume24Hr = [start_volume]

    for i in range(1,len(dk)):
        print(allk[i-1])


        if allk[i-1] in sdk:
            start_volume -= sd[allk[i - 1]]
        else:
            start_volume -= d[allk[i - 1]]

        start_volume+=d[allk[i+len(sdk)-1]]

        volume24Hr.append(start_volume)


    y = volume24Hr
        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(dk)

    return x, y


def parseBuySell(data):
    parse(data)

    print(len(data['main']))
    print(len(data['support']))

    suppdata = data['support']

    if ('interval' in data['main']):

        sd = dict((suppdata.groupby('interval').sum())['side'])
        d = dict((data['main'].groupby('interval').sum())['side'])
    else:
        sd = dict((suppdata.groupby('time').sum())['side'])
        d = dict((data['main'].groupby('time').sum())['side'])


    sdk = list(sd.keys())
    sdk.sort()
    dk = list(d.keys())
    dk.sort()

    allk = sdk+dk

    start_mood= 0
    for i in sdk:
        start_mood+=sd[i]

    buySell24Hr = [start_mood]

    for i in range(1,len(dk)):
        print(allk[i-1])


        if allk[i-1] in sdk:
            start_mood -= sd[allk[i - 1]]
        else:
            start_mood -= d[allk[i - 1]]

        start_mood+=d[allk[i+len(sdk)-1]]

        buySell24Hr.append(start_mood)


    y = buySell24Hr
        # if('interval' not in tradesDF):
        #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(dk)

    return x, y

def parseCash(data):
    parse(data)

    ids = data.groupby('time')['AbsoluteCash'].idxmax()
    netcash = data.loc[ids]['NetCashInMarket'].values
    time = data.loc[ids]['time'].values

    time = datetimeToTimeStamp(time)
    return time, netcash

def parseTradeCount(data):
    if ('interval' in data):
        #count = dict((tradesDF.groupby('interval').sum())['cash'])
        count = dict((data.groupby('interval').size()))
    else:
        #count = dict((tradesDF.groupby('time').sum())['cash'])
        count = dict(data.groupby('time').size())

    x=[]
    y=[]
    for k,v in count.items():
        x.append(k)
        y.append(v)
    x = datetimeToTimeStamp(x)
    return x,y



def txtParserAvgPrice(data):
    volume = data['volume'].sum()
    cash = data['cash'].sum()

    return cash/volume

def txtParserVolumeSum(data):
    volume = data['volume'].sum()
    return volume

def txtParserCashSum(data):
    volume = data['cash'].sum()
    return volume

def txtParserLatestPrice(data):
    price = data['price'].values[-1]
    return price
def txtParserPriceVolumeProduct(data):
    totalVolume = txtParserVolumeSum(data)
    currPrice = txtParserLatestPrice(data)
    return currPrice*totalVolume

def txtParserCashDifference(data):
    proposedAmount = txtParserPriceVolumeProduct(data)
    actualAmount = txtParserCashSum(data)

    return proposedAmount-actualAmount

def txtParserGainLossPerVolume(data):
    vol = txtParserVolumeSum(data)
    diff = txtParserCashDifference(data)

    return diff/vol



def countDigits(num):
    n = 0
    while num >0:
        num = num//10
        n+=1
    return n

def priceVolume(data, interval = None):

    min = data['price'].min()
    max = data['price'].max()

    if interval is None:
        digits = countDigits(max)
        digits -= 1
        interval = 0.1
        for i in range(digits):
            interval *= 10
        interval *= 0.1

    min = (min // interval) * interval

    prices = data['price'].values
    cats = []
    for p in prices:
        diff = p - min
        cat = min + (diff // interval) * interval
        cats.append(cat)
    data['PriceInterval'] = cats
    d = dict(data.groupby('PriceInterval').sum()['volume'])
    return d


def barGraphPriceIntervalVolumePercentage(data):

    totalVolume = txtParserVolumeSum(data)
    d = priceVolume(data)
    x= []
    y=[]
    for k,v in d.items():
        x.append(k)
        y.append(v*100/totalVolume)
    return x,y

def barGraphPriceIntervalGainLoss(data):
    x,y = barGraphPriceIntervalVolumePercentage(data)
    totalVolume = txtParserVolumeSum(data)
    currPrice = txtParserLatestPrice(data)
    for i in range(len(y)):
        y[i] = totalVolume*y[i]

    for i in range(len(y)):
        diff = currPrice- x[i]
        y[i] = y[i]*diff
    return x,y





