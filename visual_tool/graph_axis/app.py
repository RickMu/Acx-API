import sys
sys.path.append("C:\\Users\\Rick\\PycharmProjects\\Acx-API")
print(sys.path)


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore,QtGui
from collections import defaultdict
from visual_tool.client_server.http_client import HttpClient
from visual_tool.data_fetcher.client_live_data import *

class pyQtTimeGraphWrapper():

    def __init__(self,  db,ticker, rows, cols, live=False):
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("pyQTGRAPH: Tryout")
        self.graphs = []
        self.texts = []
        self.db = db
        self.client = HttpClient(db,ticker)
        self.liveupdate = ClientLiveData(db,ticker)
        self.max_row=rows
        self.max_col=cols
        self.ticker = ticker
        self.live = live


    def start(self):
        import sys

        proxy = pg.SignalProxy(self.win.sceneObj.sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.client.newData.connect(self.update)
        self.liveupdate.newData.connect(self.liveUpdate)
        self.client.start()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()



    def addGraph(self, g, row, col, colspan=1, rowspan =1, addLabel = False):

        if self.max_row <row:
            raise Exception("Greater than max row: "+ str(self.max_row))
        if self.max_col <col:
            raise Exception("Greater than max col: "+ str(self.max_col))

        self.graphs.append(g)
        self.win.addItem(g.graph,row=row, col =col,rowspan=rowspan, colspan=colspan)

        if g.buttons is not None:
            for i in range(len(g.buttons)):
                self.win.addItem(g.buttons[i],row=row,col=col+1+i)

        if (addLabel):
            label = pg.LabelItem(justify='right')
            self.win.addItem(label,row = row, col=col)
            g.setLabel(label)

    def addText(self,  t, row, col, colspan=1, rowspan =1):
        if self.max_row <row:
            raise Exception("Greater than max row: "+ str(self.max_row))
        if self.max_col <col:
            raise Exception("Greater than max col: "+ str(self.max_col))

        self.texts.append(t)
        self.win.addItem(t,row=row, col =col,rowspan=rowspan, colspan=colspan)



    def liveUpdate(self,tradesDF,suppData=None):
        for p in self.graphs:
            print('plotting again')
            if not p.needsSupportData():
                p.addData(tradesDF)


    def update(self, tradesDF, suppData):
        # getData()

        print("plotting")
        for p in self.graphs:
            if not p.needsSupportData():
                p.addData(tradesDF.copy())
            else:
                p.addData(tradesDF.copy(),suppData.copy())

        print("updating altcoin")

        for t in self.texts:
            t.setHtml(tradesDF)

        b= tradesDF.iloc[0]['id']

        if self.live:
            self.liveupdate.registerID(tradesDF.iloc[0]['id'])
            self.liveupdate.start()

    def mouseMoved(self, evt):
          ## using signal proxy turns original arguments into a tuple
        for p in self.graphs:
            p.onMouseMoved(evt)


if __name__ == "__main__":
    from visual_tool.exchange.exchange import *
    from  visual_tool.graph_axis.plot import Graph, BarGraph
    from  visual_tool.graph_axis.text import Text, CommonStyle
    from  visual_tool.data_parser.parser import *
    from visual_tool.data_parser.regression import  *

    acx = AcxExchange()
    gdx = GdxExchange()

    app = pyQtTimeGraphWrapper(gdx,GdxExchange.Ticker.BITCOIN,100,3,live= True)

    g1= Graph(supportData=False, name = "Price Graph")
    g1.addPlot(parsePrice,"price Graph")
    app.addGraph(g1,0,0,2,2,addLabel=True)

    g2= Graph(supportData=False,name = "StdDev Graph")
    g2.addPlot(parseStdDev,"StdDevGraph")
    app.addGraph(g2, 2, 0,2,2, addLabel=True)

    g3 = Graph(supportData=False,name="Volume Graph")
    g3.addPlot(parseVolume, "Volume Graph")
    #g3.addPlot(parseSideVolume, "Volume Side Graph")
    #g3.addPlot(TradeVolumeRegression().addData,can_replot=False, name ="Volume Graph Pred",color='r')
    app.addGraph(g3, 4, 0,2,2, addLabel=True)

    g4 = Graph(supportData=True, name="24Hr Volume Graph")
    g4.addPlot(parse24HrVolume, "24Hr Volume Graph")
    app.addGraph(g4, 6, 0, 2, 2, addLabel=True)

    g5 = Graph(supportData=True, name="24Hr Mood Graph")
    g5.addPlot(parseBuySell, "24Hr Mood Graph")
    app.addGraph(g5, 8, 0, 2, 2, addLabel=True)

    b1 = BarGraph(supportData=False,name="Bar Percentage Graph")
    b1.addPlot(barGraphPriceIntervalVolumePercentage, "Bar Percentage")
    #app.addGraph(b1,8,0,2,2,addLabel=True)

    b2 = BarGraph(supportData=False,name = "Bar Gain/Loss Graph")
    b2.addPlot(barGraphPriceIntervalGainLoss, "Bar Percentage")
    app.addGraph(b2, 10, 0,2,2, addLabel=True)

    t1 = Text(txtParserAvgPrice,CommonStyle.CenterText,"Avg Price",pos='left')
    app.addText(t1,12,0)

    t2 = Text(txtParserVolumeSum, CommonStyle.CenterText,"Total Volume",)
    app.addText(t2,12,0)
    t2 = Text(txtParserCashSum, CommonStyle.CenterText, "Total Cash", pos='right')
    app.addText(t2, 12, 0)

    t2 = Text(txtParserPriceVolumeProduct, CommonStyle.CenterText,"Price Volume Product", pos ='left')
    app.addText(t2, 13, 0)

    t2 = Text(txtParserCashDifference, CommonStyle.CenterText, "Gain/Loss")
    app.addText(t2, 13, 0)
    t2 = Text(txtParserGainLossPerVolume, CommonStyle.CenterText, "Gain/Loss", pos = 'right')
    app.addText(t2, 13, 0)


    app.start()