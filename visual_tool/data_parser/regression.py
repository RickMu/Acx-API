from visual_tool.data_parser.parser import TimeFormat
import pandas as pd
import collections
import math
import statsmodels.formula.api as smf

import datetime as dt
import time


class TradeVolumeRegression():

    def __init__(self):
        self.residueData = [pd.DataFrame()]
        self.SETS = 30
        self.PRED_SETS = 1
        self.INTERVALS=4
        self.MIN_INTERVALS= 5
        self.rows = None
        self.isResidue= True
        self.p = None

    def priceVolume(self,data, n=3, price_choice= 'first price', px=None):
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
            diff = 1 + math.sqrt((px[price_choice] - (min_ + i * interval)) ** 2) / (max_ - min_)
            d2[k] *= diff
            i += 1

        return d2

    def volatility(self,data):
        volume = data['volume'].values

        vola = 0
        for i in range(1, len(volume)):
            diff = abs(volume[i] - volume[i - 1])

            vola += diff

        return {
            'volatility': data.std()['volume']
        }

    def getVolumeTime(self, data):
        return {'y': data['volume'].sum(),
                'time': data.iloc[0]['time']}

    def getPrice(self,data):
        mean = data['price'].mean()
        first = data['price'].iloc[0]
        last = data['price'].iloc[len(data) - 1]
        return {'first price': first,
                'mean price': mean,
                'last price': last}

    def addData(self, data, supportData = None):


        data = TimeFormat.makeTimeIntervals(data, 'min', 5)
        #data = self.residueData + data
        dt = data.groupby('interval')

        pds = [dt.get_group(x) for x in dt.groups]
        pds = list(reversed(pds))


        if len(self.residueData+pds) < self.SETS:
            self.residueData = pds + self.residueData
            return


        '''
            if len(pds) >= missing_sets_count:
                self.residueData= self.residueData[:-1]+ pds[:missing_sets_count]
                self.pds += self.residueData
                self.residueData = []
                pds = pds[missing_sets_count+1:]
            else:
                self.residueData = self.residueData[:-1] + pds
                pds = []
        '''
        pds= pds + self.residueData
        rows_pd = []
        for i in range(len(pds)-self.SETS):
            row_pd = []
            for j in range(self.SETS):
                row_pd.append(pds[i + j])
            rows_pd.append(row_pd)

        self.residueData =  pds[:self.SETS-1]


        rows_dct = []
        for i in range(len(rows_pd)):
            y_sets = pd.concat(rows_pd[i][:self.PRED_SETS])

            px = self.getPrice(y_sets)
            x = self.priceVolume(pd.concat(rows_pd[i][self.PRED_SETS+1:]), self.INTERVALS, px= px)
            y = self.getVolumeTime(y_sets)
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
            rows_dct.append(row)

        new_rows = pd.DataFrame(rows_dct)


        if self.rows is None:
            self.rows = new_rows
        else:
            self.rows = pd.concat([self.rows,new_rows])
        self.fit()

        x = self.datetimeToTimeStamp(self.rows['time'].tolist())

        p_x, p_y = self.predict(self.residueData)

        return p_x+x, p_y+self.rows['predicted_y'].tolist()

    def datetimeToTimeStamp(self, d):
        d = [dt.datetime.strptime(i, TimeFormat.TRADES_TIME_FORMAT) for i in d]

        t = [i.timetuple() for i in d]

        timeStamp = [int(time.mktime(i)) for i in t]
        return timeStamp

    def predict(self, data):
        #data should be from self.residue

        px = self.getPrice(data[0])
        x = self.priceVolume(pd.concat(data), self.INTERVALS, 'last price', px)
        y = self.getVolumeTime(data[0])

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

        y = self.p[0]
        for i in range(1, self.INTERVALS + 1):
            y += self.p[i] * row['interval' + str(i)]


        datetm = dt.datetime.strptime(row['time'], TimeFormat.TRADES_TIME_FORMAT)


        datetm = datetm + dt.timedelta(minutes=self.PRED_SETS*self.MIN_INTERVALS)

        t = datetm.timetuple()
        x = int(time.mktime(t))

        return [x],[y]







    def function_string(self):

        int = "interval"
        string = 'y ~ interval1'

        for i in range(2,self.INTERVALS+1):
            string += "+ interval" + str(i)
        return string

    def calculate_predicted_y(self, p):

        self.rows['predicted_y'] = p[0]
        for i in range(1,self.INTERVALS+1):
            self.rows['predicted_y']+=p[i] * self.rows['interval'+str(i)]


    def fit(self):

        function = self.function_string()
        results = smf.ols(function, data=self.rows).fit()
        self.p = results.params

        print(results.summary())
        self.calculate_predicted_y(self.p)
















