#%%
import pandas as pd
import matplotlib.pyplot as plt

datasource = pd.read_csv("./12dayCoinBase.csv",squeeze= True)

datasource = datasource.drop(columns = ['id','side','cash'])

#%%
import datetime as dt
TRADES_TIME_FORMAT = "%Y-%m-%dT%H:%M"
def makeTimeIntervals(tradesDF, interval='min', time_interval=5):
    x = tradesDF['time'].values

    x = [dt.datetime.strptime(i, TRADES_TIME_FORMAT) for i in x]

    if (interval == 'min'):
        for i in range(len(x)):
            c = int(x[i].minute) // time_interval + 1

            x[i] = x[i].replace(minute=(c * time_interval - 1))
    elif (interval == 'hour'):
        for i in range(len(x)):
            c = int(x[i].hour) // time_interval + 1
            x[i] = x[i].replace(hour=(c * time_interval - 1))
            x[i] = x[i].replace(minute=(59))

    elif (interval == 'day'):
        for i in range(len(x)):
            c = int(x[i].day) // time_interval + 1

            x[i] = x[i].replace(day=(c * time_interval - 1))
            x[i] = x[i].replace(hour=24).replace(minute=59)

    x = [i.strftime(TRADES_TIME_FORMAT) for i in x]
    tradesDF['interval'] = x

    return tradesDF

datasource = makeTimeIntervals(datasource, 'min', time_interval=15)

#%%

data= datasource.groupby('interval').agg({'price':['min', 'max','mean'], 'volume':'sum'})

#%%
Periods = 5

height = data.shape[0]


def structure(name, data, initFunc, loopFunc, period= Periods):
    height = data.shape[0]
    ret = [0]*height
    
    initVal = initFunc(data, period)
    
    for i in range(period,height):
        initVal = loopFunc(data,i,period, initVal)
        ret[i] = initVal
    data[name] = ret
    return ret
        
    
def movingAvgInit(data,period):
    return sum(data['price']['mean'].values[:period])/period

def movingAvgLoopFunc(data,i,period,initVal):
    vals =data['price']['mean'].values
    initVal *=period
    initVal += (vals[i] - vals[i-period])
    return initVal/period

MA1 = structure('MA',data,movingAvgInit,movingAvgLoopFunc)


def momentumInitFunc(data,period):
    return 0

def momentumLoopFunc(data, i,period,initVal):
    vals =data['price']['mean'].values
    initVal = (vals[i] - vals[i-period])
    return initVal
Momentum = structure('momentum',data,momentumInitFunc, momentumLoopFunc)


def stochasticKInit(data,period):
    return 0

def stochasticKLoop(data,i,period,initVal):
    mean = data['price']['mean'].values
    high = data['price']['max'].values
    low = data['price']['min'].values
    
    lowest = min(low[i-period:i+1])
    highest = max(high[i-period:i+1])
    current = mean[i]
    return (current-lowest)*100/(highest-lowest)

stochasticK = structure('stochasticK',data,stochasticKInit,stochasticKLoop)

def williamRInit(data,period):
    return 0

def williamRLoopFunc(data,i,period,initVal):
    mean = data['price']['mean'].values
    high = data['price']['max'].values
    low = data['price']['min'].values
    
    lowest = min(low[i-period:i+1])
    highest = max(high[i-period:i+1])
    current = mean[i]
    return (highest-current)*100/(highest-lowest)

williamR = structure('williamR',data,williamRInit,williamRLoopFunc)

def volumeInit(data,period):
    return 0

def stochasticKVolumeLoopFunc(data,i,period,initVal):
    vols = data['volume'].values
    high = max(vols[i-period:i+1])
    low = min (vols[i-period:i+1])
    current = vols[i]
    
    return (current-low)*100/(high-low)

stochasticKVolume = structure('stochasticVolume',data,volumeInit,stochasticKVolumeLoopFunc)



#%%
%matplotlib auto
import matplotlib.pyplot as plt

x_axis = data.index.values

mean = data['price']['mean'].values
ma = data['MA'].values
sto_K = data['stochasticK'].values
         
plt.plot(mean)
plt.plot(ma)

plt.plot(sto_K)

#%%



