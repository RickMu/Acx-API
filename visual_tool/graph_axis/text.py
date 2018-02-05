import pyqtgraph as pg

class CommonStyle:

    CenterText='<div style="altcoin-align: center"><span style="color: #FF0; font-size: 16pt;">%s</span></div>'


class Text(pg.LabelItem):
    def __init__(self,parser, html, name, pos = None):
        if pos is not None:
            super().__init__(justify = pos)
        else:
            super().__init__()
        self.name= name
        self.html = html
        self.parser = parser

    def setHtml(self,data):
        val = self.parser(data)
        text = str(self.name) + ": "+self.html %(val)
        super().setText(text)

