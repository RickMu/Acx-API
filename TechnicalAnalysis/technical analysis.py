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
Periods = 14


#using rolling mechnism

def rsi(values):
    up = values[values>0].mean()
    down = -1*values[values<0].mean()
    return 100 * up / (up + down)

def movingAvg(values):
    return sum(values)/len(values)

def RSI(data,periods=Periods):
    data['diff'] = (data['price']['mean'] - data['price']['mean'].shift(1) )
    data['RSI'] = data['diff'].rolling(periods).apply(rsi).fillna(0)

def momentum(data,periods=Periods):
    data['Momentum'] =data['price']['mean']- data['price']['mean'].shift(Periods)
    
def stoKD(data,periods):
    data['STOK'] = 100*(data['price']['mean'] - pd.rolling_min(data['price']['min'],periods)) / (pd.rolling_max(data['price']['max'], periods) - pd.rolling_min(data['price']['min'],periods))
    data['STOD'] = pd.rolling_mean(data['STOK'],periods//2)
    data['STOK']=data['STOK'].fillna(0)
    data['STOD']= data['STOD'].fillna(0)

def volSTOKD(data,periods=Periods):
    
    data['VolSTOK'] = 100*(data['volume']['sum'] - pd.rolling_mean(data['volume']['sum'],periods)) / (pd.rolling_max(data['volume']['sum'], periods) - pd.rolling_min(data['volume']['sum'],periods))
    data['VolSTOD'] = pd.rolling_mean(data['VolSTOK'],periods//3)
    data['VolSTOK']=data['VolSTOK'].fillna(0)
    data['VolSTOD']= data['VolSTOD'].fillna(0)

RSI(data)
momentum(data)
data['MA'] = data['price']['mean'].rolling(Periods).apply(movingAvg).fillna(0)
stoKD(data,Periods)
volSTOKD(data)
#%%
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np

scaler = MinMaxScaler(feature_range=(0,150))

x_axis = data.index.values

mean = data['price']['mean'].values
ma = data['MA'].values
sto_K = data['STOK'].values
sto_D = data['STOD'].values
rsi = data['RSI'].values
         



mean = np.asarray(mean)
mean = mean.reshape(-1,1)
scaler = scaler.fit(mean)
mean = scaler.transform(mean)

ma= np.asarray(ma)
ma = ma.reshape(-1,1)
ma = scaler.transform(ma)

plt.plot(mean)
#plt.plot(sto_K)
plt.plot(ma)
#plt.plot(sto_D)
plt.plot(rsi)
#%%



