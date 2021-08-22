#Python -m pip install PyQtWebEngine
import pdfcreator
from PyQt5.QtWebEngineWidgets import QWebEngineView

df.sort_values(ID,ascending = False, inplace = True) #How sort dataframe

#To switch to view after click quote
main_window.tabs.setCurrentIndex(2)
main_window.tabs.widgetAt(2).tabs.addTabPage(quote_number)
#Need to make qlineedits clickable
#need to make databse headers clickable to sort
#before input dataframe, already sort by descending Quote Number


class ViewQuotes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UIComponents()

    def UIComponents(self):

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.tabs.removeTab(index))
        self.tabs.setStyleSheet("QTabBar::tab{max-height:10px;}")

        self.dock_widget = QDockWidget("Active Quotes")
        self.dock_widget.setWidget(self.tabs)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.dock_widget)

        self.dock_widget.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setDockOptions(self.GroupedDragging | self.AllowTabbedDocks | self.AllowNestedDocks)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.tabifyDockWidget(self.dock_widget,self.dock_widget)

        html = pdfcreator.getHTMLText(["CQM1-OC222", "CQM1-AD042"], [1, 2], ["New", "Used"], [1240, 1000], [1240, 2000],
                           ["In Stock", "20 Day lead time"],
                           "Kristopher Stickney", "kstickney@trwsupply.com", "082221-12051", "k@gmail.com", "RFQ Parts",
                           "08/22/2021",
                           "Credit Card", "UPS", 4000, 5000, ["New - 1 year warranty", "No warranty"])

        self.addTabPage(html,"082212-12052")

    def addTabPage(self,html,quote_number):
        view = QWebEngineView()
        view.setHtml(html)
        self.tabs.addTab(view,quote_number)