# coding: utf-8

# In[5]:

import pandas as pd
import datetime as dt
import collections
import statsmodels.formula.api as smf
import math
import numpy as np

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


# data.to_csv("./1dayCoinBase.csv")
data = pd.read_csv("./3daysCoinBase.csv")


def countDigits(num):
    n = 0
    while num > 0:
        num = num // 10
        n += 1
    return n


def priceVolume(data, n=3, px=None):
    min_ = data['price'].min()
    max_ = data['price'].max()

    interval = (max_ - min_) / n

    prices = data['price'].values
    cats = []
    for p in prices:
        diff = p - min_
        num = (diff // interval) + 1
        if num > n:
            num = n
        cats.append(num * 100 / n)

    data['PriceInterval'] = cats
    d = dict(data.groupby('PriceInterval').sum()['volume'])

    d2 = collections.OrderedDict()

    for i in range(n):
        d2[(i + 1) * 100 / n] = 0

    for k in d:
        d2[k] = d[k]

    # Here is where the scaling with profit occurs now.....
    i = 1
    for k in d2:
        diff = 1 + math.sqrt((px['first price'] - (min_ + i * interval)) ** 2) / (max_ - min_)
        d2[k] *= diff
        i += 1

    return d2


def volatility(data):
    volume = data['volume'].values

    vola = 0
    for i in range(1, len(volume)):
        diff = abs(volume[i] - volume[i - 1])

        vola += diff

    return {
        'volatility': data.std()['volume']
    }


def getVolumeTime(data):
    return {'y': data['volume'].sum(),
            'time': data.iloc[0]['time']}


def getPrice(data):
    mean = data['price'].mean()
    first = data['price'].iloc[0]
    last = data['price'].iloc[len(data) - 1]
    return {'first price': first,
            'mean price': mean,
            'last price': last}


data = makeTimeIntervals(data, 'min', 5)
dt = data.groupby('interval')

pds = [dt.get_group(x) for x in dt.groups]

split_ratio = len(pds) * 4 // 5

min = data['price'].min()
max = data['price'].max()

SET = 30
sets = []
for i in range(len(pds) - SET):
    set = []

    for j in range(SET):
        set.append(pds[i + j])

    sets.append(set)
dcts = []

intervals = 4

for i in range(len(sets)):
    y_sets = pd.concat(sets[i][SET - 5:])

    px = getPrice(y_sets)
    vola = volatility(y_sets)
    x = priceVolume(pd.concat(sets[i][:SET - 5]), intervals, px)
    y = getVolumeTime(y_sets)
    row = {}
    i = 1
    for k in x:
        row['interval' + str(i)] = x[k]
        i += 1
        row[k] = x[k]
    for k in px:
        row[k] = px[k]
    for k in y:
        row[k] = y[k]
    for k in vola:
        row[k] = vola[k]
    dcts.append(row)


mydf = pd.DataFrame(dcts)

# In[6]:

#testdf = pd.DataFrame(test)

# In[8]:

# mydf['volatility'] = (1+mydf['volatility'])*mydf['y']

results = smf.ols('y ~ interval1 + interval2 + interval3 + interval4', data=mydf).fit()
# +interval4+interval5+interval6

# Inspect the results

p = results.params

print(results.summary())

# In[9]:

mydf['predicted_y'] = p[0] + p[1] * mydf['interval1'] + p[2] * mydf['interval2'] + p[3] * mydf['interval3'] + p[4] * mydf['interval4']

#testdf['predicted_y'] = p[0] + p[1] * testdf['interval1'] + p[2] * testdf['interval2'] + p[3] * testdf['interval3'] + p[4] * testdf[ 'interval4']
# +p[5]*mydf['interval5']

# +p[6]*mydf['interval6']

# mydf['predicted_y'] = (1+mydf['volatility'])*mydf['predicted_y']


# In[10]:

import numpy as np

import matplotlib.pyplot as plt


# In[11]:
x = np.linspace(1, 20, len(mydf))

# red dashes, blue squares and green triangles
plt.plot(x, mydf['y'], 'r', x, mydf['predicted_y'], 'b')
plt.show()
# In[112]:


# In[ ]:



