from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import sys
import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit
import time

class SettingsList(QHBoxLayout):
    def __init__(self,list_items,placeholding_text = "",browse_btn=False,file_type="",file_ext=""):
        super().__init__()

        self.list = QListWidget()
        for pay in list_items:
            self.list.addItem(QListWidgetItem(pay))

        self.addition = QLineEdit()
        self.addition.setPlaceholderText(placeholding_text)
        self.addition.setObjectName("with-list")

        self.submit = QPushButton("Submit")
        self.submit.clicked.connect(self.submit_item)
        self.submit.setObjectName("with-list")

        self.delete = QPushButton("Delete")
        self.delete.clicked.connect(self.delete_item)
        self.delete.setObjectName("with-list")

        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self.browse_file(file_type,file_ext))
        browse.setObjectName("with-list")

        up = QToolButton()
        up.setArrowType(QtCore.Qt.UpArrow)
        up.clicked.connect(lambda: self.moveListItemUp(self.list))

        down = QToolButton()
        down.setArrowType(QtCore.Qt.DownArrow)
        down.clicked.connect(lambda: self.moveListItemDown(self.list))

        upup = QToolButton()
        upup.setIcon(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double up arrow.png")))
        upup.clicked.connect(lambda: self.moveListItemUp(self.list, True))

        dndn = QToolButton()
        dndn.setIcon(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double down arrow.png")))
        dndn.clicked.connect(lambda: self.moveListItemDown(self.list, True))

        grid = QGridLayout()
        if browse_btn:
            grid.addWidget(browse,0,0)
        grid.addWidget(self.submit, 1, 0)
        grid.addWidget(self.delete, 2, 0)
        grid.addWidget(up, 1, 1)
        grid.addWidget(upup, 1, 2)
        grid.addWidget(down, 2, 1)
        grid.addWidget(dndn, 2, 2)

        side_lay = QVBoxLayout()
        side_lay.addWidget(self.addition)
        side_lay.addLayout(grid)

        #payment_h_lay = QHBoxLayout()
        #payment_h_lay.addWidget(self.list)
        #payment_h_lay.addLayout(side_lay)

        self.addWidget(self.list)
        self.addLayout(side_lay)

    def moveListItemUp(self,list_,first=False):
        try:
            row = list_.currentRow()
            item = list_.takeItem(row)

            if first:
                row = 0
            else:
                row -= 1

            list_.insertItem(row, item)
            list_.setCurrentRow(row)
        except Exception as e:
            print(e)

    def moveListItemDown(self,list_,last=False):
        try:
            row = list_.currentRow()
            item = list_.takeItem(row)

            if last:
                row = list_.count()
            else:
                row += 1

            list_.insertItem(row, item)
            list_.setCurrentRow(row)
        except Exception as e:
            print(e)

    def browse_file(self,file_type,file_ext):
        try:
            file_path = QFileDialog.getOpenFileName(None, "Open "+file_type,
                                                        os.path.join(os.path.expanduser("~"), "Documents"),
                                                        file_ext)
            self.addition.setText(str(file_path[0]))
        except Exception as e:
            print(e)

    def submit_item(self):
        try:
            addition = self.addition.text()
            if addition != "":
                self.addition.clear()
                self.list.addItem(QListWidgetItem(addition))

            #stock_options.append(stock)
            #storeSettings()
        except Exception as e:
            print(e)

    def delete_item(self):
        try:
            selected_items = self.list.selectedItems()

            for item in selected_items:
                self.list.takeItem(self.list.row(item))
                #stock_options.remove(item.text())

        except Exception as e:
            print(e)

class FocusComboBox(QComboBox):
    def __init__(self,parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self,QWheelEvent):
        try:
            if (not self.hasFocus()):
                QWheelEvent.ignore()
            else:
                QComboBox.wheelEvent(self,QWheelEvent)
        except Exception as e:
            pass

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)

class CapsValidator(QValidator):
    def validate(self, string, pos):
        return QValidator.Acceptable, string.upper(), pos

class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt);
            painter.restore()


class TabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)

class CustomGridLayout(QVBoxLayout):
    def __init__(self):
        super(CustomGridLayout, self).__init__()
        self.setAlignment(QtCore.Qt.AlignTop)  # !!!
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
                lyt.setAlignment(QtCore.Qt.AlignLeft)
                lyt.setSpacing(0)
                self.addLayout(lyt)
                horLaysNr = self.count()
            ###
        ###

        # 3. Insert the widget at specified column
        self.itemAt(row).insertWidget(col, widget)

    ''''''

    def insertRow(self, row):
        lyt = QHBoxLayout()
        lyt.setAlignment(QtCore.Qt.AlignLeft)
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

#Custom QToolButton tells prices when hover
class HoverToolButton(QToolButton):
    def __init__(self,parent):
        super().__init__(parent)
        self.tooltip = PriceWindow()

    def enterEvent(self,event):
        try:
            #Get which screen application is on. use that monitor as (0,0) point.
            screen_number = QDesktopWidget().screenNumber(self)
            monitor = QDesktopWidget().screenGeometry(screen_number)
            self.tooltip.move(monitor.left()+self.x()-self.tooltip.width(),monitor.top()+self.y()+self.height()*3)
            #For some reason, x and y not meet up exactly to toolitip's edge. 3*height for y just works
        except Exception as e:
            print(e)
        self.tooltip.show()

    def leaveEvent(self,event):
        self.tooltip.hide()

    def addPriceSiteBYGRID(self, site, types, prices, stocks):
        #Inserts into grid by going through each predefined grid heading - does not allow for extra headings
        grid = self.tooltip.grid
        i = grid.rowCount()

        h = PriceWidget(site)
        h.setObjectName("header")
        grid.addWidget(h,i,0)

        for j in range(0,grid.columnCount()-1):
            text = grid.itemAtPosition(0,j+1).widget().text()

            try:
                p = PriceWidget()
                grid.addWidget(p, i, j + 1)

                index = types.index(text)
                try:
                    s = int(stocks[index][1])
                except:
                    try:
                        s = int(stocks[index])
                    except:
                        s = 0

                #p.setText("$" + str(prices[index]) + " || " + str(s))
                p.setText("${:,d} | {}".format(round(float(prices[index].replace(",",""))),s))

                if (s > 0):
                    p.setStyleSheet("background: rgb(153,204,153); color: black;")
                else:
                    p.setStyleSheet("background: rgb(251,103,103); color: black;")
            except Exception as e:
                print(e)

        #GO Through each type, which ones not put into grid, append to end


    def addPriceSite(self,site,types,prices,stocks):
        ####Goes through by each type so can add it if type is some weird label not already on grid
        grid = self.tooltip.grid
        i = grid.rowCount()

        h = PriceWidget(site)
        h.setObjectName("header")
        grid.addWidget(h, i, 0)

        index = 0
        for type in types:
            not_in_heading = False
            for j in range(1,grid.columnCount()):
                text = grid.itemAtPosition(0, j).widget().text()
                if text == type:
                    break
                elif j == grid.columnCount()-1:
                    not_in_heading = True
                    j += 1

            try:
                if not_in_heading:
                    h = PriceWidget(type)
                    h.setObjectName("header")
                    grid.addWidget(h, 0, j)

                p = PriceWidget()
                grid.addWidget(p, i, j)

                try:
                    s = int(stocks[index][1])
                except:
                    try:
                        s = int(stocks[index])
                    except:
                        s = 0

                # p.setText("$" + str(prices[index]) + " || " + str(s))
                p.setText("${:,d} | {}".format(round(float(prices[index].replace(",", ""))), s))

                if (s > 0):
                    p.setStyleSheet("background: rgb(153,204,153); color: black;")
                else:
                    p.setStyleSheet("background: rgb(251,103,103); color: black;")

                index+=1
            except Exception as e:
                index+=1
                print(e)

        #Have to go through and put in pricewidgets so not look funky
        for i in range(1,grid.rowCount()):
            for j in range(1,grid.columnCount()):
                try:
                    grid.itemAtPosition(i,j).widget()
                except:
                    grid.addWidget(PriceWidget(),i,j)

    def addPriceSiteOLD(self,site,types,prices,stocks):
        ##Sites Horizontal - no color coding
        grid = self.tooltip.grid
        j = grid.columnCount()

        grid.addWidget(PriceWidget(site), 0, j)

        for i in range(0,grid.rowCount()-1):
            text = grid.itemAtPosition(i+1,0).widget().text()

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

    def clearWindow(self):
        self.tooltip.deleteLater()
        self.tooltip = PriceWindow()
        self.tooltip.setStyleSheet_(self.styleSheet)
        self.tooltip.setWindowIcon(self.icon)

    def setWindowStylesheet(self,stylesheet):
        self.styleSheet = stylesheet
        self.tooltip.setStyleSheet_(stylesheet)
        #with open(stylesheet, "r") as fh:
            #self.tooltip.setStyleSheet(fh.read())

    def setWindowIcon(self,icon):
        self.icon = icon
        self.tooltip.setWindowIcon(icon)

#Window for HoverToolButton
class PriceWindow(QDialog):
    def __init__(self,*args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.UIComponents()



        #self.setFixedSize(700,700)
        #self.setFixedHeight(500)

    def UIComponents(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.grid.setHorizontalSpacing(0)

        #Add tags
        #self.grid.addWidget(PriceWidget(),0,0)
        i = 1
        for tag in ["New","New Opened Box","New No Box","Refurbished","Abs. New","Repair"]:
            wid = PriceWidget(tag)
            #wid.setAlignment(QtCore.Qt.AlignRight)
            wid.setObjectName("header")
            self.grid.addWidget(wid,0,i)
            i += 1

        wid = QWidget()
        wid.setLayout(self.grid)
        self.setLayout(self.grid)
        #self.setCentralWidget(wid)

    def setStyleSheet_(self,stylesheet):
        with open(stylesheet, "r") as fh:
            self.setStyleSheet(fh.read())


#Custom Widget for HoverToolButton
class PriceWidget(QLineEdit):
    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.setReadOnly(True)
        self.setAlignment(QtCore.Qt.AlignCenter)