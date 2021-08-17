from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

class CustomGridLayout(QVBoxLayout):
    def __init__(self):
        super(CustomGridLayout, self).__init__()
        self.setAlignment(Qt.AlignTop)  # !!!
        self.setSpacing(20)


    def addWidget(self, widget, row, col):
        # 1. How many horizontal layouts (rows) are present?
        horLaysNr = self.count()

        # 2. Add rows if necessary
        if row < horLaysNr:
            pass
        else:
            while row >= horLaysNr:
                lyt = QHBoxLayout()
                lyt.setAlignment(Qt.AlignLeft)
                self.addLayout(lyt)
                horLaysNr = self.count()
            ###
        ###

        # 3. Insert the widget at specified column
        self.itemAt(row).insertWidget(col, widget)

    ''''''

    def insertRow(self, row):
        lyt = QHBoxLayout()
        lyt.setAlignment(Qt.AlignLeft)
        self.insertLayout(row, lyt)

    ''''''

    def deleteRow(self, row):
        for j in reversed(range(self.itemAt(row).count())):
            self.itemAt(row).itemAt(j).widget().setParent(None)
        ###
        self.itemAt(row).setParent(None)

    def hideCol(self, col):
        for i in range(self.count()):
            try:
                self.itemAt(i).layout().itemAt(col).widget().hide()
            except: #means not enough columns in each row
                pass

    def showCol(self, col):
        for i in range(self.count()):
            try:
                self.itemAt(i).layout().itemAt(col).widget().show()
            except: #means not enough columns in each row
                pass

    def clear(self):
        for i in reversed(range(self.count())):
            for j in reversed(range(self.itemAt(i).count())):
                self.itemAt(i).itemAt(j).widget().setParent(None)
            ###
        ###
        for i in reversed(range(self.count())):
            self.itemAt(i).setParent(None)
        ###

    def columnCount(self):
        cols = self.itemAt(0).layout().count()
        return cols

    ''''''

class TableWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.rowCount = 0
        self.colCount = 0

    def addRow(self, row = -1):
        h = QHBoxLayout()
        if row == -1:
            self.main_layout.addLayout(h)
        else:
            self.main_layout.insertLayout(row,h)

        self.rowCount += 1
        return self.main_layout.indexOf(h)

    def delRow(self, row = -1):
        if row == -1:
            ind = self.main_layout.count()-1
            self.main_layout.removeItem(self.main_layout.itemAt(ind).layout())
        else:
            self.main_layout.removeItem(self.main_layout.itemAt(row).layout())

        self.rowCount -= 1

    def addCol(self,Widget, col = -1):
        if col == -1:
            for i in range(self.colCount):
                self.main_layout.itemAt(i).addWidget(QComboBox())
        else:
            for i in range(self.colCount):
                self.main_layout.itemAt(i).layout().insertWidget(col,Widget)

        self.colCount += 1

    def delCol(self, col = -1):
        if col == -1:
            ind = self.main_layout.itemAt(0).layout().count()-1
            for i in range(self.main_layout.count()): #Iterates through each HLayout
                self.main_layout.removeItem(self.main_layout.itemAt(i).layout().itemAt(ind).widget())
        else:
            for i in range(self.main_layout.count()):
                self.main_layout.removeItem(self.main_layout.itemAt(i).layout().itemAt(col).widget())

        self.colCount -= 1

    def hideCol(self, col = -1):
        if col == -1:
            ind = self.main_layout.itemAt(0).layout().count()-1
            for i in range(self.main_layout.count()): #Iterates through each HLayout
                self.main_layout.itemAt(i).layout().itemAt(ind).widget().hide()
        else:
            for i in range(self.main_layout.count()):
                self.main_layout.itemAt(i).layout().itemAt(col).widget().hide()