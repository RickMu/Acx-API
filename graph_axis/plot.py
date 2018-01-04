'''
axis bottom
label
data parsing function
'''

import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import datetime as dt

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

    def setLabel(self,label):
        self.label = label

    def addPlot(self,parser, name = None, color = 'g'):
        dataItem = self.graph.plot()

        if(name is None):
            name = self.plot_count

        self.plots[name] = dataItem
        self.plots_color[name] = color
        self.dataParser[name] = parser
        self.plot_count += 1

    def plot(self,data):

        for k,v in self.plots.items():
            x,y = self.dataParser[k](data)
            xy = {"x":x,"y":y}
            v.setData(xy, symbol='o', symbolSize=5, symbolBrush=(self.plots_color[k]))

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


    def addPlot(self, parser, name=None, color='g'):

        if (name is None):
            name = self.plot_count

        self.plots[name] = None
        self.plots_color[name] = color
        self.dataParser[name] = parser
        self.plot_count += 1

    def plot(self, data):

        for k,v in self.plots.items():

            x, y = self.dataParser[k](data)

            v = pg.BarGraphItem(x=x, height=y, width=0.4, brush=self.plots_color[k])
            self.plots[k] = v
            self.graph.addItem(v)

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
    import numpy as np

    x = np.arange(10)
    y1 = np.sin(x)
    y2 = 1.1 * np.sin(x + 1)
    y3 = 1.2 * np.sin(x + 2)

    win = pg.GraphicsWindow()
    win.setWindowTitle("pyQTGRAPH: Tryout")
    graph = pg.PlotItem()

    bg1 = pg.BarGraphItem(x=x, height=y1, width=500, brush='r')
    graph.addItem(bg1)

    win.addItem(graph)

    '''
    g = Graph()
    win.addItem(g.graph)

    '''
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()















