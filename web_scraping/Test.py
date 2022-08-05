from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from web_scraping import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UIComponents()
        self.showMaximized()

    def UIComponents(self):
        self.t = Tool()
        self.t.setMaximumSize(400, 400)
        types, prices, stocks = getRadwellPrice("cqm1-oc222")
        if types:
            self.t.addPriceSite("Radwell", types, prices, stocks)

        types, prices, stocks = getApexPLCPrice("cqm1-oc222")
        if types:
            self.t.addPriceSite("ApexPLC", types, prices, stocks)

        types, prices, stocks = getIndustrialAutomationsPrice("cqm1-oc222")
        if types:
            self.t.addPriceSite("Industrial", types, prices, stocks)
        # self.t.addPriceSite("TRW",["New No Box","New","Refurbished"],["122","245","100"],[["Stock",4],["Stock",5],["Stock",6]])

        self.setCentralWidget(self.t)


class Tool(QToolButton):
    def __init__(self):
        super().__init__()

        self.tooltip = PriceWindow()

    def enterEvent(self, event):
        self.tooltip.show()
        # self.tooltip.move(100,100)

    def leaveEvent(self, event):
        self.tooltip.hide()

    def tooltipAddSite(self, site, prices, stocks):
        grid = self.tooltip.grid
        j = grid.columnCount()

        grid.addWidget(PriceWidget(site), 0, j)

        for i in range(0, grid.rowCount() - 1):
            try:
                p = PriceWidget("$" + str(prices[i]))
                s = PriceWidget(str(stocks[i]))
                lay = QHBoxLayout()
                lay.addWidget(p)
                lay.addWidget(s)

                wid = QWidget()
                wid.setLayout(lay)

                grid.addWidget(wid, i + 1, j)
            except Exception as e:
                print(e)

    def addPriceSite(self, site, types, prices, stocks):
        grid = self.tooltip.grid
        j = grid.columnCount()

        grid.addWidget(PriceWidget(site), 0, j)

        for i in range(0, grid.rowCount() - 1):
            text = grid.itemAtPosition(i + 1, 0).widget().text()

            try:
                index = types.index(text)

                p = PriceWidget("$" + str(prices[index]))
                try:
                    s = PriceWidget(str(stocks[index][1]))
                except:
                    s = PriceWidget(str(stocks[index]))
                lay = QHBoxLayout()
                lay.addWidget(p)
                lay.addWidget(s)

                wid = QWidget()
                wid.setLayout(lay)

                grid.addWidget(wid, i + 1, j)
            except Exception as e:
                print(e)

    def addPriceSiteOLD(self, site, types_list, prices_list, stocks_list):
        grid = self.tooltip.grid
        j = grid.columnCount()

        # Reorganize lists
        new = types_list.index("New")
        nobox = types_list.index("New No Box")
        ref = types_list.index("Refurbished")
        # abs = types_list.index("Overall")
        # rep = types_list.index("Repair")

        sortedIndex = [new, nobox, ref]
        types = [types_list[i] for i in sortedIndex]
        prices = [prices_list[i] for i in sortedIndex]
        stocks = [stocks_list[i] for i in sortedIndex]

        grid.addWidget(PriceWidget(site), 0, j)

        for i in range(0, grid.rowCount() - 1):
            try:
                if types[i] is not None:
                    p = PriceWidget("$" + str(prices[i]))
                    s = PriceWidget(str(stocks[i][1]))
                    lay = QHBoxLayout()
                    lay.addWidget(p)
                    lay.addWidget(s)

                    wid = QWidget()
                    wid.setLayout(lay)

                    grid.addWidget(wid, i + 1, j)
            except:
                pass


class PriceWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)

        self.UIComponents()

        self.setFixedSize(700, 700)

    def UIComponents(self):
        self.grid = QGridLayout()

        # Add tags
        self.grid.addWidget(PriceWidget(), 0, 0)
        i = 1
        for tag in [
            "New",
            "New Opened Box",
            "New No Box",
            "Refurbished",
            "Abs. New",
            "Repair",
        ]:
            wid = PriceWidget(tag)
            wid.setAlignment(QtCore.Qt.AlignRight)
            self.grid.addWidget(wid, i, 0)
            i += 1

        wid = QWidget()
        wid.setLayout(self.grid)
        self.setCentralWidget(wid)


class PriceWidget(QLineEdit):
    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.setReadOnly(True)
        self.setAlignment(QtCore.Qt.AlignCenter)


app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
