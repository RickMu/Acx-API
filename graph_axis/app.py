


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore,QtGui
from collections import defaultdict
from client_server.http_client import HttpClient

class pyQtTimeGraphWrapper():

    def __init__(self, Acx, rows, cols):
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("pyQTGRAPH: Tryout")
        self.graphs = []
        self.texts = []
        self.Acx = Acx
        self.client = HttpClient(Acx)
        self.max_row=rows
        self.max_col=cols


    def start(self):
        import sys

        proxy = pg.SignalProxy(self.win.sceneObj.sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.client.newData.connect(self.update)
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



    def update(self, tradesDF, market):
        # getData()
        print("plotting")
        for p in self.graphs:
            p.plot(tradesDF)

        print("updating text")

        for t in self.texts:
            t.setHtml(tradesDF)

    def setMarket(self,market):
        self.client.setMarket(market)

    def mouseMoved(self, evt):
          ## using signal proxy turns original arguments into a tuple
        for p in self.graphs:
            p.onMouseMoved(evt)


if __name__ == "__main__":
    from exchange.acx_exchange import AcxExchange
    from graph_axis.plot import Graph, BarGraph
    from graph_axis.text import Text, CommonStyle
    from data_parser.parser import *
    acx = AcxExchange()

    app = pyQtTimeGraphWrapper(acx,4,3)
    app.setMarket(AcxExchange.Market.HSR)

    g1= Graph(name = "Price Graph")
    g1.addPlot(parsePrice,"price Graph")
    app.addGraph(g1,0,0,addLabel=True)

    g2= Graph(name = "StdDev Graph")
    g2.addPlot(parseStdDev,"StdDevGraph")
    app.addGraph(g2, 1, 0, addLabel=True)

    g3 = Graph(name="Volume Graph")
    g3.addPlot(parseVolume, "Volume Graph")
    app.addGraph(g3, 2, 0, addLabel=True)

    b1 = BarGraph(name="Bar Percentage Graph")
    b1.addPlot(priceIntervalVolumePercentage,"Bar Percentage")
    app.addGraph(b1,3,0,addLabel=True)

    t1 = Text(txtParserAvgPrice,CommonStyle.CenterText,"Avg Price",pos='left')
    app.addText(t1,4,0)

    t2 = Text(txtParserVolumeSum, CommonStyle.CenterText,"Total Volume",)
    app.addText(t2,3,0)

    app.start()


