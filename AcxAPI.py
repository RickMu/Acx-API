
# coding: utf-8

# In[1]:

import urllib.request
import pprint
import json
from Builders import AcxApiBuilder, Service





# In[ ]:




# In[2]:

TRADES_TIME_FORMAT = "%Y-%m-%dT%H:%M"
BTCAUD="btcaud"
BCHAUD="bchaud"
ETHAUD="ethaud"
HSRAUD="hsraud"



'''
api = AcxApiBuilder()
tickersUrl = api.service(Service.Tickers).getAPI()
print(tickersUrl)

depthUrl = api.service(Service.Depth).market(BTCAUD).AND().limit(100).getAPI()
print(depthUrl)


tradesUrl = api.service(Service.Trade).market(BTCAUD).AND().limit(100).getAPI()
print(tradesUrl)

sysTimeUrl = api.service(Service.SystemTime).getAPI()
print(sysTimeUrl)


tradesUrlFromID = api.service(Service.Trade).market(BTCAUD).AND().fromID("4115395").getAPI()

print(tradesUrlFromID)

'''

# In[3]:

def loadJSON(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
           data = json.load(response)
        return data
    except urllib.error.URLError as error:
        print(error)
        return None

import datetime as dt
import re
from collections import defaultdict
import pandas as pd

def remove(string):
    string[:-3]+string[-2:]
    return string




class Coin:
    def __init__(self,coin, roundedMeanPrice, approxVolume):
        self.coin = coin
        self.trades = defaultdict(list)
        self.audInMarket =0
        self.bought=0
        self.audOutMarket=0
        self.sold = 0
        self.recentTrades = defaultdict(list)
        self.candleStickData = defaultdict(list)
        self.newTrades = False
        self.roundedMeanPrice= roundedMeanPrice
        self.approxVolume = approxVolume

    def hasNewTrades(self):
        return self.newTrades

    def addTrades(self,trades):
        trades = list(trades)

        if(trades is None):
            print("Timed Out Error")
            self.newTrades = False
        elif (len(trades)==0):
            print('no trades')
            self.newTrades = False
        else:
            self.recentTrades.clear()
            self.recentTrades = defaultdict(list)
            
            for trade in trades:
                self.addTrade(trade)
            for k in self.recentTrades.keys():
                self.trades[k] = self.recentTrades[k]+self.trades[k]

            self.newTrades=True


        
    def addTrade(self, trade):
        TRADES_TIME_FORMAT = "%Y-%m-%dT%H:%M"

        timestr = trade['created_at']
        timestr = timestr[:16]
        print(trade['created_at'])
        struct_time = dt.datetime.strptime(timestr, TRADES_TIME_FORMAT)

        if(trade['created_at'][-1]== "Z"):
            #print(trade['created_at'])
            struct_time = struct_time + datetime.timedelta(hours=11)
        timestr = struct_time.strftime(TRADES_TIME_FORMAT)
        print(timestr)
        #struct_time = time.strptime(timestr, TRADES_TIME_FORMAT)
        
        self.recentTrades['time'].append(timestr)
        self.recentTrades['price'].append(float(trade['price']))
        self.recentTrades['id'].append(trade['id'])
       
        if(trade['trend']=='down'):
            #Both sold and audOutOfMarket is positive
            vol = -float(trade['volume'])
            cash = (vol*float(trade['price']))
            self.sold -=vol
            self.audOutMarket -= cash            
        else:
            vol = float(trade['volume'])
            cash = (vol*float(trade['price']))
            self.bought+= vol
            self.audInMarket += cash
        
        self.recentTrades['volume'].append(vol)
        self.recentTrades['cash'].append(cash)
        self.recentTrades['NetCashInMarket'].append(self.getNetAudInMarket())
        self.recentTrades['AbsoluteCash'].append(self.getAbsCashInMarket())

    
            
    def getLastTradeID(self):
        return self.recentTrades['id'][0]
        
    def isTradeRecordEmpty(self):
        return len(self.trades['id'])==0
    
    def getCandleStickRecord(self):
        tradesDF = self.getAllTradesDF()
        timeGroup = list(tradesDF.groupby('time'))
        
    
    
    def getTrades(self):
        return self.trades
    def getAllTradesDF(self):
        return pd.DataFrame(self.trades).sort_values(['time'])
    
    def getRecentTradesDF(self):
        return pd.DataFrame(self.recentTrades)
    
    def getBoughtVolume(self):
        return self.bought
    def getSoldVolume(self):
        return self.sold
    def getNetVolume(self):
        return self.bought- self.sold
    def getNetAudInMarket(self):
        return self.audInMarket-self.audOutMarket
    def getAbsCashInMarket(self):
        return self.audInMarket + self.audOutMarket



      
'''
Y year
M month
W week
D day

h hour
m minute
s seconds
ms micro seconds
...
'''


# In[4]:

import datetime
class ACX:
    def __init__(self):
        self.markets = defaultdict(Coin)
        self.apiBuilder = AcxApiBuilder()
        self.sysTime =0
        self.marketStats = defaultdict(list)
        
    def loadJSON(self,url):
        with urllib.request.urlopen(url) as response:
           data = json.load(response)
        return data
              
    def fetchMarkets(self):
        tickersUrl = self.apiBuilder.service(Service.Tickers).getAPI()
        tickers = loadJSON(tickersUrl)

        def __round__(num):
            num = int(num)
            factor = 1
            for i in range(len(str(num))-1):
                factor*=10
            num = num//factor
            num *=factor
            return num

        
        for market in tickers:

            approxMean = (float(tickers[market]['ticker']['high']) + float(tickers[market]['ticker']['low']))/2
            approxMean = __round__(approxMean)
            volume = float(tickers[market]['ticker']['vol'])//1000
            print(volume)
            volume = __round__(volume)

            print(market + str(approxMean))
            print(volume)
            self.markets[market] = Coin(market, approxMean, volume)
            
    def getMarkets(self):
        return self.markets
    
    def getMarket(self,market):
        return self.markets[market]
    
    def fetchAllTrades(self,limit):
        if (len(self.markets.keys())==0 ):
            raise Exception('No Markets Fetched, Call fetchMarkets() Before fetchingTrades')
        
        netCash = 0 
        for k in self.markets:
            self.fetchTrades(limit,k)
            netCash += self.markets[k].getNetAudInMarket()
        
        self.fetchSystemTime()
        self.marketStats['NetCash'].append(netCash)
        self.marketStats['time'].append(self.sysTime)
        
    def getMarketStatsDF(self):
        return pd.DataFrame(self.marketStats)
    
    def fetchTrades(self,limit, market):
        #Later I think should limit by using DateTime rather then limit

        if( len(self.markets.keys())==0 ):
             raise Exception('No Markets Fetched, Call fetchMarkets() Before fetchingTrades')

        if(not(market in self.markets.keys())):
            raise Exception('This market '+market +" does not exist")
            
        
        if(self.markets[market].isTradeRecordEmpty()):
            tradesUrl = self.apiBuilder.service(Service.Trade).market(market).AND().limit(limit).getAPI()
        else:
            lastTradeID = self.markets[market].getLastTradeID()
            tradesUrl = self.apiBuilder.service(Service.Trade).market(market).AND().fromID(lastTradeID).getAPI()
            
        print(tradesUrl)
        trades = loadJSON(tradesUrl)
        self.markets[market].addTrades(trades)
            
        
    def fetchSystemTime(self):
        
        systemTimeUrl = api.service(Service.SystemTime).getAPI()
        
        sysTime =  loadJSON(systemTimeUrl)
        
        readable = datetime.datetime.fromtimestamp(sysTime).isoformat()        
        self.sysTime = readable
        return self.sysTime
            


#pprint.pprint(Acx.getMarkets())



# In[ ]:




# tradesDF = btc.getAllTradesDF()
# 
# print(list(tradesDF.groupby('time')))

# In[11]:


from collections import OrderedDict

import time
def datetimeToTimeStamp(d):
    d= [dt.datetime.strptime(i,TRADES_TIME_FORMAT) for i in d]

    t = [i.timetuple() for i in d]

    timeStamp = [ int(time.mktime(i)) for i in t]
    return timeStamp


def makeTimeIntervals(tradesDF, interval = 'five_min'):

    if(interval == None):
        return
    
    x = tradesDF['time'].values
    
    x = [dt.datetime.strptime(i,TRADES_TIME_FORMAT) for i in x]
    
    if(interval == 'five_min'):
        for i in range(len(x)):
            c = int(x[i].minute)//5 +1

            x[i]= x[i].replace(minute=(c*5-1))
    elif(interval == 'hour'):
        for i in range (len(x)):
            x[i] = x[i].replace(minute=0)

    elif(interval =='day'):
        for i in range (len(x)):
            c = int(x[i].day)+1
            x[i] = x[i].replace(hour=0).replace(minute=0)

    
    x = [i.strftime(TRADES_TIME_FORMAT) for i in x]
    tradesDF['interval'] = x




def parseVolume(tradesDF):

    if('interval' in tradesDF):
        d = dict((tradesDF.groupby('interval').sum())['volume'])
    else:
        d = dict((tradesDF.groupby('time').sum())['volume'])
    print(d)


    x =[]
    y= []
    for k,v in d.items():
        x.append(k)
        y.append(v)

    #if('interval' not in tradesDF):
     #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
    x = datetimeToTimeStamp(x)

    print(dt.datetime.fromtimestamp(x[0]))
    return x,y




# In[ ]:



import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from http_client import HttpClient

class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        # if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        string = '%H:%M:%S\n %Y-%m-%d'
        label1 = '%b %d -'
        label2 = ' %b %d, %Y'

        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        # self.setLabel(text=label)
        return strns

class pyQtTimeGraphWrapper():

    PRICE_PLOT = "Price"

    VOLUME_PLOT = "Volume"

    STD_PLOT = "Std"

    TRADES_COUNT_PLOT = "Trades Count"

    TOTAL_CASH_PLOT = "Cash"
    MAJOR_MINOR_LOCATOR= {
        PRICE_PLOT: {'major': 4000, 'minor': 2000},
        VOLUME_PLOT: {'major': 4, 'minor': 1},
        TOTAL_CASH_PLOT: {'major': 1000000, 'minor': 200000}
    }



    FIVE_MIN = "five_min"
    HOUR = 'hour'
    DAY = 'day'

    def start(self):
        import sys

        proxy = pg.SignalProxy(self.win.sceneObj.sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.client.newData.connect(self.update)
        self.client.start()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def __init__(self, Acx):
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("pyQTGRAPH: Tryout")
        self.plots = []
        self.plotsData = defaultdict(dict)
        self.marketPlots = defaultdict(list)
        self.Acx = Acx
        self.client = HttpClient(Acx)
        self.row = 0

    def addPlot(self, market, type, interval, name = None,axis=None):
        if (axis is None):
            axis = DateAxis(orientation='bottom')
            axis.setTickSpacing(3600, 1800)

        label = pg.LabelItem(justify='right')
        self.win.addItem( label, row= self.row,col = 0)
        self.row+=1

        p = self.win.addPlot(row= self.row, col=0, title=name, axisItems={'bottom': axis})
        self.row+=1
        leftAxis = p.getAxis('left')

        coinMarket = self.Acx.getMarket(market)

        if(type == pyQtTimeGraphWrapper.VOLUME_PLOT):
            leftAxis.setTickSpacing(coinMarket.approxVolume, coinMarket.approxVolume*0.1 )
        elif(type == pyQtTimeGraphWrapper.PRICE_PLOT):
            leftAxis.setTickSpacing(coinMarket.roundedMeanPrice, coinMarket.roundedMeanPrice * 0.1)
        elif (type == pyQtTimeGraphWrapper.TOTAL_CASH_PLOT):
            leftAxis.setTickSpacing(pyQtTimeGraphWrapper.MAJOR_MINOR_LOCATOR[pyQtTimeGraphWrapper.TOTAL_CASH_PLOT]['major'],pyQtTimeGraphWrapper.MAJOR_MINOR_LOCATOR[pyQtTimeGraphWrapper.TOTAL_CASH_PLOT]['minor'])
        elif(type == pyQtTimeGraphWrapper.STD_PLOT):
            leftAxis.setTickSpacing(coinMarket.roundedMeanPrice, coinMarket.roundedMeanPrice * 0.005)
        elif(type == pyQtTimeGraphWrapper.TRADES_COUNT_PLOT):
            leftAxis.setTickSpacing(10, 5)


        curve1 = p.plot()
        curve2 = p.plot()

        self.plots.append(p)
        self.plotsData[p] = {'market': market, 'type': type, 'curve': [curve1,curve2], 'interval': interval}
        self.marketPlots[market].append(p)
        self.client.addMarket(market)


        self.plotsData[p]['label'] = label
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        p.addItem(vLine, ignoreBounds=True)
        p.addItem(hLine, ignoreBounds=True)
        self.plotsData[p]['cross'] = [vLine, hLine]

        return p



    def update(self, tradesDF, market):
        # getData()
        plotsOfThisMarket = self.marketPlots[market]

        for p in plotsOfThisMarket:
            makeTimeIntervals(tradesDF, interval=self.plotsData[p]['interval'])
            color = "g"
            #print('intervals done')
            if (self.plotsData[p]['type'] == pyQtTimeGraphWrapper.VOLUME_PLOT):
                x, y = self.parseVolume(tradesDF)
            elif (self.plotsData[p]['type'] == pyQtTimeGraphWrapper.PRICE_PLOT):
                x, y = self.parsePrice(tradesDF)
            elif(self.plotsData[p]['type'] == pyQtTimeGraphWrapper.TOTAL_CASH_PLOT):
                x, y = self.parseCash(tradesDF)
            elif (self.plotsData[p]['type'] == pyQtTimeGraphWrapper.STD_PLOT):
                x, y = self.parseSTD(tradesDF)
                color = "w"
            elif(self.plotsData[p]['type'] == pyQtTimeGraphWrapper.TRADES_COUNT_PLOT):
                x, y = self.parseTradeCount(tradesDF)

            #print('parses done for plot :'+ self.plotsData[p]['type'])
            xy = {'x': x, 'y': y}
            self.plotsData[p]['curve'][0].setData(xy, symbol='o', symbolSize=10, symbolBrush=(color))


    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        for p in self.plots:
            if p.sceneBoundingRect().contains(pos):
                mousePoint = p.vb.mapSceneToView(pos)
                index = int(mousePoint.x())
                #print( dt.datetime.fromtimestamp(mousePoint.x()).strftime("%Y-%m-%d %H:%M:%S"))


                string = dt.datetime.fromtimestamp(mousePoint.x()).strftime("%Y-%m-%d %H:%M:%S")

                self.plotsData[p]['label'].setText(
                    "<span style='color: red'>y1=%s</span>,   <span style='color: green'>y2=%0.1f</span>"
                    % (string,mousePoint.y()))


                self.plotsData[p]['cross'][0].setPos(mousePoint.x())
                self.plotsData[p]['cross'][1].setPos(mousePoint.y())


    def parsePrice(self, tradesDF):
        '''
        Needs fixing this price parse shit'''
        if ('interval' in tradesDF):
            d = dict((tradesDF.groupby('interval').mean())['price'])
        else:
            d = dict((tradesDF.groupby('time').mean())['price'])

        x = []
        y = []

        for k, v in d.items():
            x.append(k)
            y.append(v)

            # if('interval' not in tradesDF):
            #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
        x = datetimeToTimeStamp(x)

        print(dt.datetime.fromtimestamp(x[0]))
        return x, y

    def parseSTD(self,tradesDF):
        if ('interval' in tradesDF):
            s = dict((tradesDF.groupby('interval').std())['price'])
        else:
            s = dict((tradesDF.groupby('time').std())['price'])

        sx = []
        sy = []


        for k, v in s.items():
            sx.append(k)
            sy.append(v)

            # if('interval' not in tradesDF):
            #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
        sx = datetimeToTimeStamp(sx)
        return sx, sy

    def parseVolume(self, tradesDF):

        if ('interval' in tradesDF):
            d = dict((tradesDF.groupby('interval').sum())['volume'])
        else:
            d = dict((tradesDF.groupby('time').sum())['volume'])
        print(d)

        x = []
        y = []
        for k, v in d.items():
            x.append(k)
            y.append(v)

            # if('interval' not in tradesDF):
            #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
        x = datetimeToTimeStamp(x)

        print(dt.datetime.fromtimestamp(x[0]))
        return x, y

    def parseCash(self, tradesDF):

        ids = tradesDF.groupby('time')['AbsoluteCash'].idxmax()
        print(ids.values)
        netcash = tradesDF.loc[ids]['NetCashInMarket'].values
        time = tradesDF.loc[ids]['time'].values

        time = datetimeToTimeStamp(time)
        print(dt.datetime.fromtimestamp(time[0]))
        return time, netcash

    def parseTradeCount(self,tradesDF):
        #tradesDF['Cash'] = tradesDF['price']*tradesDF['volume']
        if ('interval' in tradesDF):
            #count = dict((tradesDF.groupby('interval').sum())['cash'])
            count = dict((tradesDF.groupby('interval').size()))
        else:
            #count = dict((tradesDF.groupby('time').sum())['cash'])
            count = dict(tradesDF.groupby('time').size())

        x=[]
        y=[]
        for k,v in count.items():
            x.append(k)
            y.append(v)
        x = datetimeToTimeStamp(x)
        return x,y






'''
        d = dict((tradesDF.groupby('time').sum())['NetCashInMarket'])
        print(d)

        x = []
        y = []
        for k, v in d.items():
            x.append(k)
            y.append(v)

            # if('interval' not in tradesDF):

            #   x= [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]
'''


def run():
    Acx = ACX()
    Acx.fetchMarkets()
    graphWrapper =pyQtTimeGraphWrapper(Acx)

    #graphWrapper.addPlot(BTCAUD,pyQtTimeGraphWrapper.VOLUME_PLOT,pyQtTimeGraphWrapper.HOUR)
    graphWrapper.addPlot(BTCAUD,pyQtTimeGraphWrapper.PRICE_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Mean Price Vs Five_Min Time ")
    graphWrapper.addPlot(BTCAUD,pyQtTimeGraphWrapper.STD_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Strd Deviation Vs Five_Min Time")
    graphWrapper.addPlot(BTCAUD,pyQtTimeGraphWrapper.VOLUME_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "NetVolume Vs Five_Min Time")
    graphWrapper.addPlot(BTCAUD,pyQtTimeGraphWrapper.TRADES_COUNT_PLOT,None, name = "Trade Count Vs 1_Min Time")

    #graphWrapper.addPlot(HSRAUD,pyQtTimeGraphWrapper.PRICE_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Mean Price Vs Five_Min Time")
    #graphWrapper.addPlot(HSRAUD,pyQtTimeGraphWrapper.STD_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Strd Deviation Vs Five_Min Time")
    #graphWrapper.addPlot(HSRAUD,pyQtTimeGraphWrapper.VOLUME_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "NetVolume Vs Five_Min Time")
    #graphWrapper.addPlot(HSRAUD,pyQtTimeGraphWrapper.TRADES_COUNT_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "NetCash Vs Five_Min Time")

    #graphWrapper.addPlot(ETHAUD,pyQtTimeGraphWrapper.PRICE_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Mean Price Vs Five_Min Time")
    #graphWrapper.addPlot(ETHAUD,pyQtTimeGraphWrapper.STD_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "Strd Deviation Vs Five_Min Time")
    #graphWrapper.addPlot(ETHAUD,pyQtTimeGraphWrapper.VOLUME_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "NetVolume Vs Five_Min Time")
    #graphWrapper.addPlot(ETHAUD,pyQtTimeGraphWrapper.TOTAL_CASH_PLOT,pyQtTimeGraphWrapper.FIVE_MIN, name = "NetCash Vs Five_Min Time")

    graphWrapper.start()

if __name__ == "__main__":
    run()

'''
win = pg.GraphicsWindow()
win.setWindowTitle("pyQTGRAPH: Tryout")


label = pg.LabelItem(justify='right')
win.addItem(label)
p = win.addPlot()
c1 = p.plot({'x':[1,2,3],'y':[2,3,4]})
c2 = p.plot({'x':[1,2,3],'y':[6,7,8]})


label.setText(
"<span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>"
% (10000, 1000000))

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

'''


'''

Acx = ACX()
Acx.fetchMarkets()
Acx.fetchTrades(1000,BTCAUD)
btc = Acx.getMarket(BTCAUD)
tradesDF = btc.getAllTradesDF()
makeTimeIntervals(tradesDF, interval='hour')
x, y = parseVolume(tradesDF)
pyQtDataFormat = defaultdict(list)
pyQtDataFormat['x'] = x
pyQtDataFormat['y'] = y

maxY = 2


win = pg.GraphicsWindow()
win.setWindowTitle("pyQTGRAPH: Tryout")
axis = DateAxis(orientation='bottom')
axis.setTickSpacing(3600,1800)
#axis.setTickSpacing(2*3600,2)
p1 = win.addPlot(axisItems={'bottom': axis})

c1 = p1.plot(pyQtDataFormat)





def getData():
    Acx.fetchTrades(100, BTCAUD)
    tradesDF = Acx.getMarket(BTCAUD).getAllTradesDF()
    makeTimeIntervals(tradesDF, interval='hour')
    x, y = parseVolume(tradesDF)
    pyQtDataFormat['x'] = x
    pyQtDataFormat['y'] = y
    print(x)


def plot(xyDict):
    if((xyDict  is not None)):
        c1.setData(xyDict, symbol='o', symbolSize=10, symbolBrush=("g"))

        #c1.setPos(min(xyDict['x'])+3600,0)



def update(xyDict=None):
    #getData()
    plot(xyDict)

'''
'''

th = DataThread()
th.newData.connect(update)
th.start()


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

'''



'''

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np

# FIXME: When running on Qt5, not as perfect as on Qt4

win = pg.plot()
win.setWindowTitle('pyqtgraph example: FillBetweenItem')
win.setXRange(-10, 10)
win.setYRange(-10, 10)

N = 200
x = np.linspace(-10, 10, N)
gauss = np.exp(-x ** 2 / 20.)
mn = mx = np.zeros(len(x))
curves = [win.plot(x=x, y=np.zeros(len(x)), pen='k') for i in range(4)]
brushes = [0.5, (100, 100, 255), 0.5]
fills = [pg.FillBetweenItem(curves[i], curves[i + 1], brushes[i]) for i in range(3)]
for f in fills:
    win.addItem(f)


def update():
    global mx, mn, curves, gauss, x
    a = 5 / abs(np.random.normal(loc=1, scale=0.2))
    y1 = -np.abs(a * gauss + np.random.normal(size=len(x)))
    y2 = np.abs(a * gauss + np.random.normal(size=len(x)))

    s = 0.01
    mn = np.where(y1 < mn, y1, mn) * (1 - s) + y1 * s
    mx = np.where(y2 > mx, y2, mx) * (1 - s) + y2 * s
    curves[0].setData(x, mn)
    curves[1].setData(x, y1)
    curves[2].setData(x, y2)
    curves[3].setData(x, mx)


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(30)

QtGui.QApplication.instance().exec_()

'''

