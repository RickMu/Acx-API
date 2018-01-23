'''
axis bottom
label
data parsing function
'''

import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import datetime as dt
from data_parser.parser import TimeFormat

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



class Graph():

    def __init__(self,name=None, title=None, axisItem = None):
        print('start')
        self.plot_count = 0
        self.plots={}
        self.plots_color={}
        self.dataParser= {}
        if axisItem is None:
            axisItem = DateAxis(orientation='bottom')
            axisItem.setTickSpacing(3600, 1800)
        self.bottomAxis = axisItem
        self.graph = pg.PlotItem(name=name,title=title,axisItems={'bottom': axisItem})

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graph.addItem(self.vLine, ignoreBounds=True)
        self.graph.addItem(self.hLine, ignoreBounds=True)
        self.label =None

        self.data= None
        self.buttons =None

    def setLabel(self,label):
        self.label = label

    def addPlot(self,parser, name = None, color = 'g'):
        dataItem = self.graph.plot()
        self.addStandardButtons()

        rgn = pg.LinearRegionItem(bounds = [0.3, 0.35])
        self.graph.addItem(rgn)

        if(name is None):
            name = self.plot_count

        self.plots[name] = dataItem
        self.plots_color[name] = color
        self.dataParser[name] = parser
        self.plot_count += 1


    def plot(self,data):

        if self.data is None:
            self.data = data
        for k,v in self.plots.items():
            v.clear()
            x,y = self.dataParser[k](data)
            xy = {"x":x,"y":y}
            v.setData(xy, symbol='o', symbolSize=5, symbolBrush=(self.plots_color[k]))


    def addStandardButtons(self):

        b0 = QtGui.QPushButton('Back')
        b1 = QtGui.QPushButton('5min')
        b2 = QtGui.QPushButton('30min')
        b3 = QtGui.QPushButton('1hour')
        self.buttons = [b1, b2, b3]

        width = b0.fontMetrics().boundingRect('Back').width() + 7
        b0.setMaximumWidth(width)

        width = b1.fontMetrics().boundingRect('5min').width() + 7
        b1.setMaximumWidth(width)

        width = b1.fontMetrics().boundingRect('30min').width() + 7
        b2.setMaximumWidth(width)

        width = b1.fontMetrics().boundingRect('1hour').width() + 7
        b3.setMaximumWidth(width)

        b0.clicked.connect(lambda: self.replot(None,None))
        b1.clicked.connect(lambda:self.replot( 'min',5))
        b2.clicked.connect(lambda: self.replot( 'min', 30))
        b3.clicked.connect(lambda: self.replot( 'hour', 1))

        btns = [b0,b1,b2,b3]
        self.buttons=[]
        for b in btns:
            proxy = QtGui.QGraphicsProxyWidget()
            proxy.setWidget(b)
            self.buttons.append(proxy)



    def replot(self, time_unit,interval):

        if time_unit is None and interval is None:
            self.plot(self.data)
            return

        cp = self.data.copy()
        data = TimeFormat.makeTimeIntervals(cp,time_unit,interval)
        self.plot(data)


    def onMouseMoved(self,evt):

        if (self.label is None):
            return
        pos = evt[0]
        if self.graph.sceneBoundingRect().contains(pos):
            mousePoint = self.graph.vb.mapSceneToView(pos)

            string = dt.datetime.fromtimestamp(mousePoint.x()).strftime("%Y-%m-%d %H:%M:%S")

            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

            self.label.setText(
                "<span style='color: red'>y1=%s</span>,   <span style='color: green'>y2=%0.1f</span>"
                % (string, mousePoint.y()))

class RegionSelectionGraph(Graph):
    def __init__(self,name=None, title=None, axisItem = None):
        print('start')
        self.plot_count = 0
        self.plots = {}
        self.plots_color = {}
        self.dataParser = {}
        if axisItem is None:
            axisItem = DateAxis(orientation='bottom')
            axisItem.setTickSpacing(3600, 1800)
        self.bottomAxis = axisItem
        self.graph = pg.PlotItem(name=name, title=title, axisItems={'bottom': axisItem})

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graph.addItem(self.vLine, ignoreBounds=True)
        self.graph.addItem(self.hLine, ignoreBounds=True)
        self.label = None

    def addPlot(self, parser, name=None, color='g'):
        dataItem = self.graph.plot()
        rgn = pg.LinearRegionItem([0.3, 0.5])
        self.graph.addItem(rgn)

        if (name is None):
            name = self.plot_count

        self.plots[name] = dataItem
        self.plots_color[name] = color
        self.dataParser[name] = parser
        self.plot_count += 1

    def plot(self, data):

        if self.data is None:
            self.data = data
        for k, v in self.plots.items():
            v.clear()
            x, y = self.dataParser[k](data)
            xy = {"x": x, "y": y}
            v.setData(xy, symbol='o', symbolSize=5, symbolBrush=(self.plots_color[k]))




class BarGraph(Graph):
    def __init__(self,name=None, title=None):
        print('start')
        self.plot_count = 0
        self.plots={}
        self.plots_color={}
        self.dataParser= {}
        self.graph = pg.PlotItem(name=name,title=title)

        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graph.addItem(self.vLine, ignoreBounds=True)
        self.graph.addItem(self.hLine, ignoreBounds=True)
        self.label =None
        self.buttons = None


    def addPlot(self, parser, name=None, color='g'):
        #self.addStandardButtons()

        if (name is None):
            name = self.plot_count

        self.plots[name] = None
        self.plots_color[name] = color
        self.dataParser[name] = parser
        self.plot_count += 1

    def plot(self, data):

        for k,v in self.plots.items():
            x, y = self.dataParser[k](data)
            if(len(x)>1):
                width = x[1]-x[0]
            width = 0.4*width
            v = pg.BarGraphItem(x=x, height=y, width=width, brush=self.plots_color[k])
            self.plots[k] = v
            self.graph.addItem(v)

    def addStandardButtons(self):

        # Create textbox
        textbox = QtGui.QLineEdit()
        textbox.setFixedWidth(100)

        # Create a button in the window
        button = QtGui.QPushButton('Set Interval')

        # connect button to function on_click
        button.clicked.connect(lambda :self.redraw(textbox))

        width = button.fontMetrics().boundingRect('1hour').width() + 7
        button.setMaximumWidth(width)

        p1 = QtGui.QGraphicsProxyWidget()
        p1.setWidget(textbox)

        p2 =QtGui.QGraphicsProxyWidget()
        p2.setWidget(button)
        self.buttons=[p1,p2]

    def redraw(self, textbox):
        textbox.text()
        print(textbox.text())


    def onMouseMoved(self,evt):

        if (self.label is None):
            return
        pos = evt[0]
        if self.graph.sceneBoundingRect().contains(pos):
            mousePoint = self.graph.vb.mapSceneToView(pos)

            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

            self.label.setText(
                "<span style='color: red'>y1=%0.01f</span>,   <span style='color: green'>y2=%0.01f</span>"
                % (mousePoint.x(), mousePoint.y()))


if __name__ == "__main__":

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()















