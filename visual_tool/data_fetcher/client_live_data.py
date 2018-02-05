from visual_tool.builder_clients.api_clients import GDXApiClient
import pyqtgraph as pg



import time



class ClientLiveData(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object,object)

    def __init__(self, db,ticker):

        super().__init__()
        self.conn = GDXApiClient()
        self.ticker = ticker
        self.lastID = None
        self.db = db


    def registerID(self,id):
        self.lastID = id

    def run(self):
        while True:
            time.sleep(8)
            print('fetching trades')
            data = self.conn.fetchTrades(self.ticker,self.lastID)

            m = self.db.coins[self.ticker]
            m.addTrades(data)
            trades = m.getRecentTradesDF()
            self.lastID =  trades.iloc[0]['id']
            self.newData.emit(trades, None)


