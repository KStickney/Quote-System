#Settings: Allow how many columns, what size each column, if combobox or pure plugin, if and where completer draw from
import sys

import pandas
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import math
import pickle
import os
import subprocess
import threading
import time
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
#from qt_material import apply_stylesheet #KYLE NOT LIKE LAYOUT
import logging as log


from CustomClasses import *
from pdf.pdfcreator import *
from database import *
from web_scraping.web_scraping import *

#Default Settings
default_SAVE_QUOTES_DIRECTORY = "C:/Users/Patrick/Desktop/"
default_FIRST_TIME = True
#default_payment_terms = {"Credit Card":"CC","NET 30":"NET 30","NET 45":"NET45","NET 60":"NET 60","Wire Transfer":"TT","Paypal":"PayPayl",
                         #"Other":"Other","Credit Card, Wire Transfer, or Paypal":"Credit Card, Wire Transfer, or Paypal"}
default_payment_terms = ["Credit Card, Wire Transfer, or Paypal","Credit Card","NET 30","NET45","NET 60","Wire Transfer","Paypal","Other"]
default_shipping_methods = ["","UPS Ground","UPS NDA","UPS 2nd NDA","FedEx Ground","FedEx NDA","DLH"]
default_table_headers = ["Item","Quantity", "Part Number","Condition","Unit Price","Line Total","Stock","Notes"]
default_initial_part_rows = 3 #How many rows show initially in quote
default_database_headers = ["Quote Number","Customer Email","Part Number",]
default_sample_notes = ["New Warranty -- 1 year", "New Surplus Warranty -- 1 year", "Refurbished Warranty -- 1 year","Surplus Never Used Warranty -- 1 year","*****************************"]
default_senders = {"Kyle Stickney":"kstickney@trwsupply.com",
                   "Nathan Christensen": "nchristensen@trwsupply.com"
                   }
default_preferred_search = "Part"
default_theme = "Dark, Orange"
default_alternating_color = "rgb(231,231,227)" #TODO: Link css file to these so when change all alternate ones change
default_alternating_font = "black"
default_stock_options = ["In Stock","Ships in 1-2 Days","Ships in 2-3 Days","Ships in 3-4 Days","Ships in 1 Week","Ships in 1-2 Weeks",
                         "Ships in 2 Weeks","Ships in 2-3 Weeks","4-8 Weeks","Out of Stock","Call",
                         "N/A"]
default_part_conditions = ["New","New Surplus","Surplus, Never Used","Refurbished","Repair","Other"]
default_database_searches = ["Subject","Quote_Number","Part_Number"]

#Regular variables
completer_list = ["Germany", "Spain", "France", "Norway","Norwegian"] #TODO: Make completer both inline and popup
completer = QCompleter(completer_list)
completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
completer.setCompletionMode(QCompleter.PopupCompletion)

DATABASE_HEADERS = []
DATABASE_FILE = "./TRW Quote Database.csv"
ALTERNATING_COLORS = {
                "dark, orange": ("rgb(231,231,227)","black"),
                "dark, blue": ("rgb(120,135,155)","black"),
                "classic": ("rgb(228,246,248)","black"),
                "dark": ("rgb(231,231,227)","black"),
                "light": ("rgb(231,231,227)","black"),
            } #dark_blue rgb(231,231,227)
default_local_settings = {
    "Database Headers": default_database_headers,
    "Preferred Search": default_preferred_search,
    "Theme": default_theme,
    "Alternating Color": default_alternating_color,
    "Alternating Font": default_alternating_font,
    "First Time": default_FIRST_TIME,
    "Quote Directory": default_SAVE_QUOTES_DIRECTORY,
    "Database Searches": default_database_searches,
}
default_shared_settings = {
    "Payment Terms": default_payment_terms,
    "Shipping Methods": default_shipping_methods,
    "Table Headers": default_table_headers,
    "Initial Part Rows": default_initial_part_rows,
    "Sample Notes": default_sample_notes,
    "Senders": default_senders,
    "Part Conditions": default_part_conditions,
    "Stock Options": default_stock_options,
}
default_settings = {
    "Payment Terms": default_payment_terms,
    "Shipping Methods": default_shipping_methods,
    "Table Headers": default_table_headers,
    "Initial Part Rows": default_initial_part_rows,
    "Database Headers": default_database_headers,
    "Sample Notes": default_sample_notes,
    "Senders": default_senders,
    "Preferred Search": default_preferred_search,
    "Theme": default_theme,
    "Alternating Color": default_alternating_color,
    "Alternating Font": default_alternating_font,
    "First Time": default_FIRST_TIME,
    "Quote Directory": default_SAVE_QUOTES_DIRECTORY,
    "Part Conditions": default_part_conditions,
    "Stock Options": default_stock_options,
    "Database Searches": default_database_searches,
}
#settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/settings.pickle") #For pickle, could put all variables inside dictionary or list or use editorconfig file
local_settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/local_settings.pickle")
first_time_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/first_time.txt")
#database_settings_file = "./data/database.pickle"
database_settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/database.pickle")


class MainWindow(QMainWindow): #TODO: make function for when click into and out of each tab + warning message box for Quote tab
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TRW Quote System")
        logo = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),'images/TRW Supply Logo.jpg'))
        self.setWindowIcon(logo)

        self.styleSheet = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stylesheets/Main Stylesheet.css")
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.UIComponents()
        self.showMaximized()

    def UIComponents(self):

        self.tabs = TabWidget()#QTabWidget()
        self.tabs.addTab(Database(), "Database")
        self.tabs.addTab(ActiveQuote(),"Active Quote")
        self.tabs.setTabEnabled(1,False)
        self.tabs.addTab(ViewQuotes(), "View Quotes")
        self.tabs.addTab(Settings(),"Settings")

        self.tabs.tabBarClicked.connect(self.handleTabbarClicked)

        self.setCentralWidget(self.tabs)

    def handleTabbarClicked(self,index):
        #self.tabs.tabText(index)
        try:
            #if index == 1: #Active Quote #When click on Active Quote tab, inputs quote number and subject
                #if self.tabs.widget(index).invoice_number.text() == "":
                 #   number = getNewInvoiceNumber()
                  #  self.tabs.widget(index).invoice_number.setText(number)

                   #self.tabs.widget(index).subject.setText("RFQ")

            if index == 0: #Databse
                self.tabs.widget(index).submit_search_keep_place()

            if index == 2: #View Quotes
                if not self.tabs.widget(index).dock_widget.isVisible():
                    self.tabs.widget(index).dock_widget.setVisible(True)
                    self.tabs.widget(index).dock_widget.setFloating(False)
                    #TODO: Why Not Putting it back to floating??
                if self.tabs.widget(index).dock_widget.isFloating():
                    self.tabs.widget(index).dock_widget.setFloating(False)
        except Exception as e:
            sendMessage("Main Window Tabs Clicked",str(e),self)

class ActiveQuote(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stylesheets/Quote Stylesheet.css")
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.table_row_count = 0

        #last date/time edited
        self.last_time_edited = datetime.now()

        self.UIComponents()

    def UIComponents(self):
        try:
            #Invoice Header
            invoice_label = QLabel("Quote Number: ")
            invoice_label.setObjectName("invoice")
            invoice_label.setMaximumWidth(125)

            self.invoice_number = QLineEdit()
            self.invoice_number.setPlaceholderText("Invoice Number")
            self.invoice_number.setObjectName("invoice")
            self.invoice_number.setReadOnly(True)

            self.sent_from_label = QLabel("Sent From:")
            self.sent_from_label.setObjectName("invoice")
            self.sent_from_label.setAlignment(QtCore.Qt.AlignVCenter)
            self.sent_from_label.setMaximumWidth(87)

            #self.sent_from = QComboBox()
            self.sent_from = FocusComboBox(self)
            self.sent_from.addItems(senders.keys())
            self.sent_from.setCurrentText(DEFAULT_USER)

            subj = QLabel("Subject: ")
            subj.setObjectName("invoice")
            subj.setMaximumWidth(75)

            self.subject = QLineEdit()
            self.subject.setObjectName("subject")

            lay = QHBoxLayout()
            lay.setSpacing(0)
            lay.addWidget(self.sent_from_label)
            lay.addWidget(self.sent_from)

            lay2 = QHBoxLayout()
            lay2.setSpacing(0)
            lay2.addWidget(invoice_label)
            lay2.addWidget(self.invoice_number)

            lay3 = QHBoxLayout()
            lay3.setSpacing(0)
            lay3.addWidget(subj)
            lay3.addWidget(self.subject)

            self.invoice_layout = QHBoxLayout()
            self.invoice_layout.addLayout(lay2)
            self.invoice_layout.addLayout(lay3)
            self.invoice_layout.addLayout(lay)


            #CUSTOMER INFO
            cust_name = QLabel("Customer Name:")
            cust_name.setObjectName("customer")
            self.customer_name = QLineEdit()
            self.customer_name.setPlaceholderText("Customer Name")
            self.customer_name.setObjectName("customer")
            lay1 = QHBoxLayout()
            lay1.addWidget(cust_name)
            lay1.addWidget(self.customer_name)

            cust_email = QLabel("Customer Email:")
            cust_email.setObjectName("customer")
            self.customer_email = QLineEdit()
            self.customer_email.setPlaceholderText("Customer Email")
            self.customer_email.setObjectName("customer")
            lay2 = QHBoxLayout()
            lay2.addWidget(cust_email)
            lay2.addWidget(self.customer_email)

            cust_phone = QLabel("Customer Phone:")
            cust_phone.setObjectName("customer")
            self.customer_phone = QLineEdit()
            self.customer_phone.setPlaceholderText("Customer Phone")
            self.customer_phone.setObjectName("customer")
            lay3 = QHBoxLayout()
            lay3.addWidget(cust_phone)
            lay3.addWidget(self.customer_phone)

            layout = QVBoxLayout()
            layout.setSpacing(0)
            for item in (lay1,lay2,lay3):
                layout.addLayout(item)


            self.customer_info = QTextEdit()
            self.customer_info.setObjectName("customer")
            self.customer_info.setPlaceholderText("Customer Info")

            self.customer_layout = QHBoxLayout()
            self.customer_layout.addLayout(layout)
            self.customer_layout.addWidget(self.customer_info)


            #SHIPPING
            p = QLabel("Payment Terms:")
            s = QLabel("Shipping Method:")
            sc = QLabel("Shipping Charges:")
            for label in (p,s,sc):
                label.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignRight)
                label.setObjectName("shipping")

            self.payment_terms = FocusComboBox(self)
            self.payment_terms.setEditable(False)
            self.payment_terms.addItems(PAYMENT_TERMS)

            self.shipping_method = FocusComboBox(self)
            self.shipping_method.setEditable(False)
            self.shipping_method.addItems(SHIPPING_METHODS)

            self.shipping_charges = QLineEdit()
            #self.shipping_charges.setValidator(QDoubleValidator())
            self.shipping_charges.installEventFilter(self)

            for item in (self.payment_terms,self.shipping_method,self.shipping_charges):
                item.setObjectName("shipping")

            self.wire_transfer = QCheckBox("Pro Forma Invoice")
            #self.wire_transfer.setObjectName("wire") #For before put into note_group

            lay1 = QHBoxLayout()
            lay1.addWidget(p)
            lay1.addWidget(self.payment_terms)

            lay2 = QHBoxLayout()
            lay2.addWidget(s)
            lay2.addWidget(self.shipping_method)

            lay3 = QHBoxLayout()
            lay3.addWidget(sc)
            lay3.addWidget(self.shipping_charges)

            shipping_layout = QHBoxLayout()
            shipping_layout.addLayout(lay1)
            shipping_layout.addLayout(lay2)
            shipping_layout.addLayout(lay3)
            #shipping_layout.addWidget(self.wire_transfer)


            #Where table grid used to be
            #ITEM TABLE
            self.add_table_item_btn = QPushButton("Add Item")
            self.add_table_item_btn.setObjectName("add-item")
            self.add_table_item_btn.clicked.connect(lambda: self.addTableRow(i=None, remove_btn=True))

            self.del_table_item_btn = QPushButton("Delete Item")
            self.del_table_item_btn.setObjectName("add-item")
            self.del_table_item_btn.clicked.connect(lambda: self.deleteTableItem())

            self.add_note_btn = QCheckBox("Add Note")
            self.add_note_btn.setObjectName("add-item")
            #self.add_note_btn.toggled.connect(lambda: self.addNoteCol())
            self.add_note_btn.toggled.connect(lambda: self.toggleNoteCol())
            self.add_note_btn.setChecked(False)

            self.get_prices_btn = QPushButton("Get Prices")
            self.get_prices_btn.setObjectName("add-item")
            self.get_prices_btn.clicked.connect(lambda: self.getPriceToolTip())

            #PART NUMBER TABLE
            self.table = QGridLayout()
            self.table.setSpacing(0)
            self.table.setAlignment(QtCore.Qt.AlignCenter)
            for i in range(INITIAL_PART_ROWS):
                self.addTableRow(i)

            self.subtotal_price = QLineEdit()
            self.subtotal_price.setObjectName("total")
            self.total_price = QLineEdit()
            self.total_price.setObjectName("total")

            subtotal_label = QLabel("Subtotal: ")
            total_label = QLabel("Total: ")
            for btn in (subtotal_label,total_label):
                btn.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
                btn.setObjectName("total")

            grid = QGridLayout()
            grid.setSpacing(0)
            grid.setAlignment(Qt.AlignCenter)
            grid.addWidget(subtotal_label,0,0)
            grid.addWidget(total_label, 1,0)
            grid.addWidget(self.subtotal_price,0,1)
            grid.addWidget(self.total_price,1,1)

            #self.addNoteCol()
            btn_lay = QHBoxLayout()
            btn_lay.setAlignment(QtCore.Qt.AlignLeft)
            btn_lay.setSpacing(10)
            self.table_buttons = [self.add_table_item_btn,self.del_table_item_btn,self.add_note_btn,self.get_prices_btn]
            for btn in self.table_buttons:
                btn_lay.addWidget(btn)

            self.grid_lay = QVBoxLayout()
            self.grid_lay.setSpacing(0)
            self.grid_lay.setStretch(0,0)
            self.grid_lay.addLayout(self.table)
            self.grid_lay.addLayout(grid)
            self.grid_lay.addLayout(btn_lay)

            self.note_group = QGroupBox("Notes") #Group Box for the quote notes
            self.note_group.setCheckable(False)
            self.note_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred) #.Preferred
            self.note_group_grid = QGridLayout()
            self.note_group.setLayout(self.note_group_grid)
            NOTE_COLS = 3
            NOTE_ROWS = math.ceil((len(sample_notes)+1) / NOTE_COLS) #Rounds up so another col is not created
            i = 1
            j=0
            self.note_group_grid.addWidget(self.wire_transfer, 0, 0)
            for k in range(len(sample_notes)): #Populates the grid layout
                box = QCheckBox(sample_notes[k],self.note_group)
                box.clicked.connect(lambda:self.note_checkbox_state())
                if i >= NOTE_ROWS:
                    j+=1
                    i = 0
                self.note_group_grid.addWidget(box,i,j)
                i += 1

            self.additional_info_label = QLabel("Additional Info")
            self.additional_info_label.setAlignment(QtCore.Qt.AlignLeft)
            self.additional_infos = QTextEdit()
            self.additional_infos.setPlaceholderText("Additional Info")
            self.additional_infos.setObjectName("info")
            self.additional_info_layout = QVBoxLayout()
            self.additional_info_layout.setSpacing(0)
            self.additional_info_layout.addWidget(self.additional_info_label)
            self.additional_info_layout.addWidget(self.additional_infos)

            self.additional_info_out_layout = QVBoxLayout() #Make one layout for the group,label, and text box so closer together
            self.additional_info_out_layout.addWidget(self.note_group)
            self.additional_info_out_layout.addLayout(self.additional_info_layout)

            self.save_btn = QPushButton("Save")
            self.save_btn.clicked.connect(lambda: self.saveQuote())

            self.save_and_exit_btn = QPushButton("Save and Close")
            self.save_and_exit_btn.clicked.connect(lambda: self.saveAndClose())

            self.close_btn = QPushButton("Close")
            self.close_btn.clicked.connect(self.Close)

            self.save_PDF_btn = QPushButton("Create PDF")
            self.save_PDF_btn.clicked.connect(self.createPDF)

            self.submit_layout = QHBoxLayout()
            for btn in (self.save_btn,self.save_and_exit_btn,self.close_btn,self.save_PDF_btn):
                self.submit_layout.addWidget(btn)
                btn.setObjectName("submit")

            #MAIN LAYOUT
            self.main_layout = QVBoxLayout() #The main layout for the quote part of the app
            self.main_layout.setSpacing(30)
            self.main_layout.addLayout(self.invoice_layout)
            self.main_layout.addLayout(self.grid_lay)
            self.main_layout.addLayout(self.customer_layout)
            self.main_layout.addLayout(shipping_layout)
            self.main_layout.addLayout(self.additional_info_out_layout)
            self.main_layout.addLayout(self.submit_layout)


            widget = QWidget()
            widget.setLayout(self.main_layout)

            self.scroll_area = QScrollArea()  # Allows app to scroll
            self.scroll_area.setWidgetResizable(True)
            #self.scroll_area.setLayout(self.main_layout)
            self.scroll_area.setWidget(widget)

            self.vlayout = QVBoxLayout()
            self.vlayout.addWidget(self.scroll_area)
            self.setLayout(self.vlayout)
        except Exception as e:
            sendMessage("Active Quote GUI Setup",str(e),self)

    def note_checkbox_state(self):
        btn = self.sender()
        index = self.note_group_grid.indexOf(btn)
        btn = self.note_group_grid.itemAt(index).widget()
        if btn.isChecked():
            self.additional_infos.append(btn.text())

        else:
            text = self.additional_infos.toPlainText()
            text = text.replace(btn.text() + " ", "")
            text = text.replace(btn.text() + "\n", "")
            text = text.replace("\n"+btn.text(), "")
            text = text.replace("\n" + btn.text() + "\n", "")
            text = text.replace(btn.text(), "")
            self.additional_infos.setText(text)

    def addTableRow(self,i,remove_btn = False):
        try:
            total_rows = 0
            for row in range(self.table.rowCount()):
                try:
                    int(self.table.itemAtPosition(row, 1).widget().text())
                    total_rows += 1
                except:
                    pass
            action = 1
            if self.table_row_count > 20:
                msg = QMessageBox()
                msg.setWindowTitle("Too many Rows")
                msg.setText("There are 20 parts, after which number the parts will not show on the quote. "
                                            "Do you wish to proceed?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                action = msg.exec()
            if action == QMessageBox.Yes or action == 1:
                if remove_btn:
                    #for btn in self.table_buttons:
                        #self.table.removeWidget(btn)
                    #i = self.table_row_count - 1
                    #self.table_row_count -= 1
                    #pass
                    #i = self.table_row_count

                    ##This would work, except if user deleted numbers
                    #i=self.table.rowCount()
                    rows = self.table.rowCount()
                    nextNum = 0
                    for row in range(1,rows):
                        try:
                            current = int(self.table.itemAtPosition(row,1).widget().text())
                            if current >= nextNum:
                                nextNum = current + 1
                        except:
                            pass
                            #Just means that there is not actually a row there
                    i = nextNum

                    insert_row = self.table.rowCount()
                else:
                    insert_row = i
                ##i denotes what row person sees
                ##insert_row denotes to the grid to insert row after last row that it sees


                #wid = QCheckBox()
                #if i == 0:
                    #sp_retain = wid.sizePolicy()
                    #sp_retain.setRetainSizeWhenHidden(True)
                    #wid.setSizePolicy(sp_retain)
                    #wid.hide()
                #self.table.addWidget(wid, i, 0)



                for j in range(len(table_headers)):

                    if i == 0:  # Means Header
                        cell = QLineEdit()
                        cell.setAlignment(QtCore.Qt.AlignCenter)
                        cell.setReadOnly(True)
                        cell.setObjectName("table-header")
                        cell.setText(table_headers[j])

                        if j == 0: #means "ITEM" Header
                            cell.setFixedWidth(80)
                        if j == 1: #QUANTITY
                            cell.setFixedWidth(100)
                        if table_headers[j] == "Condition" or table_headers[j] == "Stock":
                            cell.setObjectName("header-combo")
                        if table_headers[j] == "Line Total" or table_headers[j] == "Unit Price":
                            cell.setMaximumWidth(200)
                        if table_headers[j] == "Part Number":
                            cell.setMaximumWidth(500)
                        if j == (len(table_headers) - 1) and not self.add_note_btn.isChecked():  # Hide Notes Column
                            cell.hide()
                    else:

                        if table_headers[j] == "Condition": #CONDITIONS
                            cell = FocusComboBox(self)
                            cell.addItems(part_conditions)
                        elif table_headers[j] == "Stock": #STOCK
                            cell = FocusComboBox(self)
                            cell.addItems(stock_options)
                        #elif table_headers[j] == "Line Total" or table_headers[j] == "Unit Price":
                        elif False: #FOR IF USE QDOUBLESPINBOX for line total and unit price - not used because would have to change anything that gets/set Text
                            cell = QDoubleSpinBox()
                            cell.setAlignment(QtCore.Qt.AlignCenter)
                            cell.setPrefix("$")
                            cell.setMaximum(4500)
                            cell.setMaximumWidth(200)
                            cell.setButtonSymbols(QAbstractSpinBox.NoButtons)
                        elif table_headers[j] == "Line Total" or table_headers[j] == "Unit Price":
                            cell = QLineEdit()
                            cell.setAlignment(QtCore.Qt.AlignCenter)
                            cell.setMaximumWidth(200)
                        else:
                            cell = QLineEdit()
                            cell.setAlignment(QtCore.Qt.AlignCenter)

                        if table_headers[j] == "Part Number":
                            cell.setValidator(CapsValidator())
                            cell.setCompleter(getCompleter("Part"))
                            cell.setMaximumWidth(500)

                            #Set event filter that gets the info prices tooltip once lose mouse focus
                            #cell.installEventFilter(self) ##For multithreading getting prices- Freezes GUI

                        if j == 0: #ITEM number
                            cell.setFixedWidth(80)
                            cell.setReadOnly(True)
                            cell.setText(str(i))
                        if j == 1: #Quantity only accept integers
                            cell.setValidator(QIntValidator())
                            cell.setFixedWidth(100)
                        if j == 1 or j == 4 or j == 5: #make quantity and unity price change line total4
                            cell.installEventFilter(self)
                            #cell.textChanged.connect(lambda: self.calculateLineTotal()) #Need add source;
                            pass
                        if j == (len(table_headers) - 1) and not self.add_note_btn.isChecked():  # Hide Notes Column
                            cell.hide()

                        # Note - cell.setObjectName has to be after the setStyleSheet line
                        if i % 2 == 1:
                            cell.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                        cell.setObjectName("table")


                    self.table.addWidget(cell,insert_row,j+1)

                #insert checkbox, price info box if not header
                if i != 0:
                    ##Checkbox
                    wid = QCheckBox(self)
                    wid.setMaximumWidth(20)
                    self.table.addWidget(wid, insert_row, 0)
                    ##price info button for each row
                    info = HoverToolButton(self)
                    info.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/info.png")))
                    info.setObjectName("table")
                    info.setWindowStylesheet(os.path.join(os.path.dirname(os.path.realpath(__file__)),"stylesheets/Prices Stylesheet.css"))
                    info.setStyleSheet("background: rgb(170,175,180);")
                    info.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),'images/TRW Supply Logo.jpg')))
                    # alternate colors
                    #if i % 2 == 1:
                        #info.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    self.table.addWidget(info, insert_row, j + 2)

                self.table_row_count += 1

                #if remove_btn:
                    #i = self.table_row_count + 1
                    #self.addTableButtons(i)

        except Exception as e:
            sendMessage("Active Quote GUI Setup",str(e),self)

    def eventFilter(self, source, event):
        try:
            if (event.type() == QtCore.QEvent.FocusOut):
                if source == self.shipping_charges:
                    self.formatShippingCharges()
                else:
                    self.calculateLineTotal(source)
                pass
            return super(ActiveQuote, self).eventFilter(source, event)
        except Exception as e:
            print(e)

    def getPriceToolTip(self):
        try:
            driver = getDriver()

            for i in range(1,self.table.rowCount()):
                try:
                    part = self.table.itemAtPosition(i,3).widget().text()
                    btn = self.table.itemAtPosition(i, 9).widget()
                    btn.clearWindow()
                    btn.setStyleSheet("background: rgb(170,175,180);")
                    if part != "":

                        yl_new_df = getYLNewPrice(part)
                        yl_ref_df = getYLRefPrice(part)

                        mfr_df = getMFRPrice(part)

                        a_types, a_prices, a_stocks = getApexPLCPrice(part,driver)
                        r_types, r_prices, r_stocks = getRadwellPrice(part)
                        i_types, i_prices, i_stocks = getIndustrialAutomationsPrice(part,driver)

                        list_ = [["ApexPLC", a_types, a_prices, a_stocks],["Radwell", r_types, r_prices, r_stocks],
                                ["Industrial", i_types, i_prices, i_stocks]]
                        if not yl_new_df.empty:
                            btn.addPriceSite("Charles", ["New", "Refurbished"],
                                             [str(yl_new_df.iloc[0]["YL_New_Price"]), str(yl_ref_df.iloc[0]["YL_Ref_Price"])],[1,1])
                            btn.setStyleSheet("background: rgb(30,146,244);")

                        if not mfr_df.empty:
                            btn.addPriceSite("Manufacturer",["New"],[str(mfr_df.iloc[0]["Manufacturer_Price"])],[1])
                            btn.setStyleSheet("background: rgb(30,146,244);")

                        for li in list_:
                            if li[1]:  # If list not empty
                                btn.addPriceSite(li[0], li[1], li[2], li[3])
                                btn.setStyleSheet("background: rgb(30,146,244);")
                except Exception as e:
                    sendMessage("Price Tool Tip",str(e),self)

            driver.close()
        except Exception as e:
            sendMessage("Price Tool Tip",str(e),self)
            try:
                driver.close()
            except:
                pass

    def formatShippingCharges(self):
        try:
            text = self.shipping_charges.text().replace("$","")
            if text == "" or text == "$":
                self.shipping_charges.setText("")
            else:
                self.shipping_charges.setText("${:.2f}".format(float(text)))

            self.calculateQuoteTotal()
        except Exception as e:
            sendMessage("Format Shipping Charges", "Please Input an Actual Number", self)
            self.shipping_charges.setText("")

    def calculateLineTotal(self,btn):
        try:
            #iterate through each cell one to find what row it is in
            try:
                for row in range(1,self.table.rowCount()):
                    for col in range(self.table.columnCount()):
                        try:
                            #If statements throws error when delete row because then row exists but widget doesn't. Why need two try-except statements
                            if self.table.itemAtPosition(row,col).widget() == btn:
                                index = row
                                column = col
                                raise Found
                        except Exception as e:
                            pass
            except Found:
                pass

            if column in (2,5):
                ##CALCULATE LINE TOTAL USING QUANTITY AND UNIT PRICE

                #get quantity
                quantity = self.table.itemAtPosition(index,2).widget().text()
                if quantity == "":
                    quantity = 0
                else:
                    quantity = int(quantity)

                #get unit price
                unit = self.table.itemAtPosition(index,5).widget().text().replace("$","")
                if unit == "":
                    unit = 0
                else:
                    unit = float(unit)
                    # put unit price back in formatted to two decimal places
                    #self.table.itemAt(index).layout().itemAt(5).widget().setText(str(format(unit, '.2f')))
                    #taken out - won't let keep typing

                #insert line total formated to two decimal places
                #self.table.itemAt(index).layout().itemAt(6).widget().setText(str(format(quantity *unit, '.2f')))
                self.table.itemAtPosition(index,6).widget().setText(str("$" + format(quantity * unit, '.2f')))
                self.table.itemAtPosition(index, 5).widget().setText(str("$" + format(unit, '.2f')))

                #For if use QDoubleSpinBox
                #self.table.itemAtPosition(index, 6).widget().setValue(quantity*unit)

            elif column == 6:
                ##CALCULATE UNIT TOTAL USING QUANTITY AND LINE PRICE

                # get quantity
                quantity = self.table.itemAtPosition(index, 2).widget().text()
                if quantity == "":
                    quantity = 0
                else:
                    quantity = int(quantity)

                # get unit price
                line_total = self.table.itemAtPosition(index, 6).widget().text().replace("$", "")
                if line_total == "":
                    line_total = 0
                else:
                    line_total = float(line_total)

                # insert line total formated to two decimal places
                try:
                    unit_price = line_total / quantity
                except:
                    # divide by 0
                    unit_price = line_total
                    self.table.itemAtPosition(index, 2).widget().setText("1")

                self.table.itemAtPosition(index, 5).widget().setText(str("$" + format(unit_price, '.2f')))
                self.table.itemAtPosition(index, 6).widget().setText(str("$" + format(line_total, '.2f')))

            self.calculateQuoteTotal()

        except Exception as e:
            sendMessage("Calculate Line Total",str(e),self)
            try:
                self.table.itemAtPosition(index, 5).widget().setText("")
            except:
                pass

    def calculateQuoteTotal(self):
        try:
            #Puts total prices into subtotal and total boxes
            subtotal = 0
            for row in range(1, self.table.rowCount()):
                try:
                    subtotal += float(self.table.itemAtPosition(row, 6).widget().text().replace("$", ""))
                except:
                    pass
            self.subtotal_price.setText(str("$" + format(subtotal, '.2f')))
            shipping_charges = self.shipping_charges.text().replace("$", "")
            if shipping_charges == "":
                shipping_charges = 0
            else:
                shipping_charges = float(shipping_charges)
            self.total_price.setText(str("$" + format(subtotal + shipping_charges, '.2f')))
        except Exception as e:
            print(e)


    def addTableButtons(self,i):
        for j in range(len(self.table_buttons)):
            v = QHBoxLayout()
            v.addWidget(self.table_buttons[j])
            v.setStretch(1,0)
            self.table.addWidget(self.table_buttons[j],i,j+1)
            self.table.addItem(v,i,j+1)
        self.table_row_count+=1

    def addTableButtons2(self,i):
        wid = QCheckBox()
        sp_retain = wid.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        wid.setSizePolicy(sp_retain)
        wid.hide()
        self.table.addWidget(wid,i,0)
        for j in range(len(self.table_buttons)):
            self.table.addWidget(self.table_buttons[j],i,j+1)
        self.table.itemAt(i).layout().setSpacing(15)
        self.table_row_count += 1

    def checkTableCheckboxes(self):
        try:
            rows = []
            for row in range(self.table.rowCount()):
                try:
                    if self.table.itemAtPosition(row,0).widget().isChecked():
                        rows.append(row)
                except:
                    pass
        except:
            pass
        return rows

    def checkTableCheckboxes2(self):
        try:
            rows = []
            for row in range(self.table.count()-1):
                try:
                    if self.table.itemAt(row).layout().itemAt(0).widget().isChecked():
                        rows.append(row)
                except Exception as e:
                    pass
        except Exception as e:
            pass
        return rows

    def deleteTableItem(self):
        try:
            rows = self.checkTableCheckboxes()
            for i in rows:
                for j in range(self.table.columnCount()):
                    try:
                        self.table.itemAtPosition(i,j).widget().deleteLater()
                        #self.table.removeWidget(self.table.itemAtPosition(i,j).widget())
                    except:
                        pass
                self.table_row_count -= 1
        except Exception as e:
            print(e)

        try:
            num = 1
            for i in range(1,self.table.rowCount()):
                try:
                    self.table.itemAtPosition(i,1).widget().setReadOnly(False)
                    self.table.itemAtPosition(i,1).widget().setText(str(num))
                    self.table.itemAtPosition(i, 1).widget().setReadOnly(True)
                    num += 1

                    for j in range(1,self.table.columnCount()):
                        if num%2 == 0:
                            self.table.itemAtPosition(i,j).widget().setStyleSheet(f"""background: {Alternating_color}; color: {Alternating_font};""")
                        else:
                            self.table.itemAtPosition(i,j).widget().setStyleSheet("")
                except Exception as e:
                    pass
        except Exception as e:
            print(e)


    def deleteTableItemREDO(self): #Completely gets rid and implements back in. Need to find a way to replace self.table, since saying self.table = QGridLayout() doesn't work to make a new instance
        ##Have to take all info out, delete table, and reinsert it
        try:
            rows = self.checkTableCheckboxes()
            info = []
            for i in range(1,self.table.rowCount()):
                if i not in rows:
                    info.append([])
                    for j in range(2,self.table.columnCount()): #don't need checkbox or item number
                        try:
                            info[-1].append(self.table.itemAtPosition(i,j).widget().text())
                        except:
                            try:
                                info[-1].append(self.table.itemAtPosition(i, j).widget().currentText())
                            except:
                                pass

            if self.table is not None:
                while self.table.count():
                    item = self.table.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            #self.grid_lay.removeItem(self.table)

            #self.table = QGridLayout()
            #self.table.setSpacing(0)
            #self.table.setAlignment(QtCore.Qt.AlignCenter)

            #self.grid_lay.insertItem(0,self.table)
            self.addTableRow(0)


        except Exception as e:
            print(e)

    def toggleNoteCol(self):
        j = self.table.columnCount()-2

        if self.add_note_btn.isChecked():
            for i in range(self.table.rowCount()):
                try:
                    self.table.itemAtPosition(i,j).widget().show()
                except:
                    pass
        else:
            for i in range(self.table.rowCount()):
                try:
                    self.table.itemAtPosition(i,j).widget().hide()
                except:
                    pass

    def addNoteCol(self): #TODO: Check see if already have note box, change j to always be same column
        try:
            j = self.table.columnCount()-1

            if self.add_note_btn.isChecked():
                for i in range(self.table.rowCount()):
                    try:
                        self.table.itemAtPosition(i,j).widget().show()
                    except:
                        pass

            else:
                for i in range(self.table.rowCount()):
                    try:
                        self.table.itemAtPosition(i, j).widget().hide()
                    except:
                        pass
        except Exception as e:
            print(e)

    def saveAndClose(self):
        try:
            self.submitQuote()
            self.Close(save=True)

            #Resubmit search in Database tab - to update
            main_window.tabs.widget(0).onSubmitSearch()
        except Exception as e:
            print(e)

    def Close(self,save=False): #save, if true, means coming from saveAndClose()
        try:
            action = ""
            if not save:
                msg = QMessageBox()
                msg.setWindowTitle("Save and Continue")
                msg.setText("Would you like to save the quote before exiting?")
                msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
                action = msg.exec()

            if action == QMessageBox.Cancel:
                pass
            else:
                if action == QMessageBox.Yes:
                    self.submitQuote()
                quote_number = main_window.tabs.widget(1).invoice_number.text()

                updateIsEditing(quote_number,False)

                main_window.tabs.removeTab(1)
                main_window.tabs.insertTab(1, ActiveQuote(), "Active Quote")
                main_window.tabs.setCurrentIndex(0)
                main_window.tabs.setTabEnabled(1,False)

        except Exception as e:
            sendMessage("Close Quote",str(e),self)
            if save: #save means coming from method saveAndClose() - want to raise Exception so won't continue to close
                raise Exception


    def createPDF(self):
        try:
            #First save/update quote to database
            self.submitQuote()

            quote_number = self.invoice_number.text()

            df = getQuote(self.invoice_number.text())

            html = getHTMLText(str(df["Part_Number"].values[0]).split(';'), str(df["Quantity"].values[0]).split(';'),
                                   str(df["Condition"].values[0]).split(';'),
                                   str(df["Unit_Price"].values[0]).split(';'), str(df["Line_Total"].values[0]).split(';'),
                                   str(df["Stock"].values[0]).split(';'),
                                   str(df["Sender"].values[0]), str(df["Sender_Email"].values[0]),
                                   str(df["Quote_Number"].values[0]), str(df["Customer_Email"].values[0]),
                                   str(df["Subject"].values[0]), str(df["_Date"].values[0]),
                                   str(df["Payment_Terms"].values[0]),
                                   str(df["Shipping_Method"].values[0]), str(df["Additional_Notes"].values[0]).split("\n"),
                                    df.iloc[0]["Pro_Forma"],df.iloc[0]["Shipping_Charges"],df.iloc[0]["Customer_Notes"])

            path = SAVE_QUOTES_DIRECTORY+"/"+str(df["Quote_Number"].values[0])
            makeQuotePDF(html,path)\

            pdf = path+".pdf"

            #open pdf
            subprocess.Popen([pdf],shell=True)
        except Exception as e:
            sendMessage("Create PDF",str(e),self)

    def saveQuote(self):
        try:
            self.submitQuote()
        except Exception as e:
            sendMessage("Save Quote",str(e),self)

    def submitQuote(self):

       #to convert "None" to Proper None:    x = None if x == 'None' else x

        #for row in range(1, self.table.count() - 1): #Checks to see if missing info #TODO: Do we want this??
            #for col in range(2, self.table.itemAt(row).count()):
                #if self.table.itemAt(row).layout().itemAt(col).widget().text() == "":
                    #sendMessage("Missing Info",
                                #"There are columns with missing information. Would you like to continue?",parent = main_window)

        quote_number = self.invoice_number.text()


        #if datetime user has with quote is less than the one in the database - means someone else has changed it already
        action = ""
        try:
            if getQuoteLastEdited(quote_number) > self.last_time_edited: #For is is editing
                msg = QMessageBox()
                msg.setText("Another User has updated this quote since you started editing.\nWould you like to still submit?")
                msg.setWindowTitle("Not most current edit")
                msg.setIcon(QMessageBox.Critical)
                msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                action = msg.exec()
        except:
            pass

        if action != QMessageBox.No:

            self.last_time_edited = datetime.now()

            quantities = ""
            part_numbers = ""
            conditions = ""
            unit_prices = ""
            line_totals = ""
            stocks = ""
            notes = ""

            for row in range(1,self.table.rowCount()):
                try:
                    if self.table.itemAtPosition(row,3).widget().text() != "": #if there is a part number, then save row
                        if self.table.itemAtPosition(row,2).widget().text() != "":
                            quantities += self.table.itemAtPosition(row,2).widget().text() + ";"
                        else:
                            #quantities += "None;"
                            quantities += '0;'

                        part_numbers += self.table.itemAtPosition(row,3).widget().text() + ";"

                        if self.table.itemAtPosition(row,4).widget().currentText() != "":
                            conditions += self.table.itemAtPosition(row,4).widget().currentText() + ";"
                        else:
                            conditions += "None;"
                        if self.table.itemAtPosition(row,5).widget().text() != "":
                            unit_prices += self.table.itemAtPosition(row,5).widget().text() + ";"
                        else:
                            #unit_prices += "None;"
                            unit_prices += "0;"
                        if self.table.itemAtPosition(row,6).widget().text() != "":
                            line_totals += self.table.itemAtPosition(row,6).widget().text() + ";"
                        else:
                            #line_totals += "None;"
                            line_totals += "0;"
                        if self.table.itemAtPosition(row,7).widget().currentText() != "":
                            stocks += self.table.itemAtPosition(row,7).widget().currentText() + ";"
                        else:
                            stocks += "None;"
                        if self.table.itemAtPosition(row,8).widget().text() != "":
                            notes += self.table.itemAtPosition(row,8).widget().text() + ";"
                        else:
                            notes += "None;"
                except:
                    pass

            #delete semicolon at end
            try:
                quantities = quantities[:-1]
                part_numbers = part_numbers[:-1]
                conditions = conditions[:-1]
                unit_prices = unit_prices[:-1].replace("$","")
                line_totals = line_totals[:-1].replace("$","")
                stocks = stocks[:-1]
                notes = notes[:-1]
            except Exception as e:
                pass

            subject = self.subject.text()

            sender = self.sent_from.currentText()

            sender_email = senders[sender]

            customer_name = self.customer_name.text()

            customer_email = self.customer_email.text()

            customer_phone = self.customer_phone.text()

            customer_notes = self.customer_info.toPlainText()

            additional_notes = self.additional_infos.toPlainText()

            payment_terms = self.payment_terms.currentText()

            shipping_method = self.shipping_method.currentText()

            shipping_charges = self.shipping_charges.text().replace("$","")

            pro_forma = self.wire_transfer.isChecked()

            submitQuoteToDatabase(quote_number=quote_number,quantities=quantities,part_numbers=part_numbers,
                                  conditions=conditions,unit_prices=unit_prices,line_totals=line_totals,stock=stocks,
                                  notes=notes,subject=subject,sender=sender,sender_email=sender_email,customer_name=customer_name,customer_email=customer_email,
                                  customer_phone=customer_phone,customer_notes=customer_notes,additional_notes=additional_notes,
                                  payment_terms=payment_terms,shipping_method=shipping_method,shipping_charges=shipping_charges,pro_forma=pro_forma,
                                  last_edited=self.last_time_edited)

            #Update new part numbers in database
            parts = part_numbers.split(";")
            updatePartNumbers(parts)


    def getTableItemContents(self,row,j):
        if self.table.itemAtPosition(row, j).widget().text() != "":
            return self.table.itemAtPosition(row, j).widget().text() + ";"
        else:
            return "None;"


class ViewQuotes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UIComponents()
        self.showMaximized()

    def UIComponents(self):
        try:
            self.tabs = QTabWidget()
            self.tabs.setTabsClosable(True)
            self.tabs.tabCloseRequested.connect(lambda index: self.tabs.removeTab(index))
            self.tabs.setStyleSheet("QTabBar::tab{max-height:10px;}")

            self.dock_widget = QDockWidget("Active Quotes")
            self.dock_widget.setWidget(self.tabs)

            print = QPushButton("Create PDF")
            print.setMaximumSize(120,30)
            print.clicked.connect(self.printQuote)

            edit = QPushButton("Edit")
            edit.setMaximumSize(120,30)
            edit.clicked.connect(self.editQuote)

            copy = QPushButton("Copy Quote")
            copy.setMaximumSize(120,30)
            copy.setMinimumSize(120,30)
            copy.clicked.connect(self.copyQuote)

            lay = QHBoxLayout()
            lay.addWidget(print)
            lay.addWidget(edit)
            lay.addWidget(copy)

            wid = QWidget()
            wid.setLayout(lay)
            wid.setMaximumHeight(50)

            self.setCentralWidget(wid)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock_widget)
            self.setLayout(QVBoxLayout())

            #Don't really know what do - nothing seems to change - saw on internet
            #self.dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
            #self.setDockOptions(self.GroupedDragging | self.AllowTabbedDocks | self.AllowNestedDocks)
            #self.setTabPosition(QtCore.Qt.AllDockWidgetAreas, QTabWidget.North)
            #self.tabifyDockWidget(self.dock_widget,self.dock_widget)

        except Exception as e:
            sendMessage("View Quote GUI Setup", str(e), self)

    def addTabPage(self,html,quote_number):
        view = QWebEngineView()
        view.setHtml(html)
        self.tabs.addTab(view,quote_number)

        index = self.tabs.indexOf(view)
        self.tabs.setCurrentIndex(index)

        view.page().runJavaScript("C:/Users/Patrick/Documents/Kristopher Programming/Quote-System/pdf/js/actions.js")

    def printQuote(self):
        try:
            tab = self.tabs.currentWidget()
            tab.page().runJavaScript("document.getElementsByTagName('html')[0].innerHTML", self.makePDF)

            #QWebEngineView has own way to make PDF - used to be below format
            #path = SAVE_QUOTES_DIRECTORY + "/" + self.tabs.tabText(self.tabs.currentIndex())
            #self.tabs.currentWidget().page().printToPdf(path)
        except Exception as e:
            sendMessage("Print Quote",str(e),self)

    def makePDF(self,html):
        path = SAVE_QUOTES_DIRECTORY + "/" + self.tabs.tabText(self.tabs.currentIndex())
        makeQuotePDF(html, path)

        pdf = path + ".pdf"
        # open pdf
        subprocess.Popen([pdf], shell=True)

    def editQuote(self):
        try:
            # IF same quote already in Active Quote Tab
            if main_window.tabs.widget(1).invoice_number.text() == str(self.tabs.tabText(self.tabs.currentIndex())):
                main_window.tabs.setCurrentIndex(1)  # switch to active quote tab
            elif main_window.tabs.widget(1).invoice_number.text() != "":
                action = main_window.tabs.widget(0).sendQuoteInUseMsg()

                if action == QMessageBox.Yes:
                    main_window.tabs.widget(1).submitQuote()
                    self.continueEditQuote()
                if action == QMessageBox.No:
                    self.continueEditQuote()
            else:
                self.continueEditQuote()

        except Exception as e:
            sendMessage("Copy Quote",str(e),self)

    def continueEditQuote(self):
        # get quote from database
        #df = getQuote(self.tabs.tabText(self.tabs.currentIndex()))
        quote_number = self.tabs.tabText(self.tabs.currentIndex())

        # insert quote into edit
        main_window.tabs.widget(0).continueEditQuote(quote_number, editing=True)

    def copyQuote(self):
        try:

            if main_window.tabs.widget(1).invoice_number.text() != "":
                action = main_window.tabs.widget(0).sendQuoteInUseMsg()

                if action == QMessageBox.Yes:
                    main_window.tabs.widget(1).submitQuote()
                    self.continueCopyQuote()
                if action == QMessageBox.No:
                    self.continueCopyQuote()
            else:
                self.continueCopyQuote()

        except Exception as e:
            sendMessage("Copy Quote",str(e),self)

    def continueCopyQuote(self):
        try:
            # get quote from database
            df = getQuote(self.tabs.tabText(self.tabs.currentIndex()))

            # get new quote number
            invoice_number = getNewInvoiceNumber()

            # insert quote into edit
            main_window.tabs.widget(0).continueEditQuote(0, df, editing=False)

            # insert new quote number and subject
            main_window.tabs.widget(1).invoice_number.setText(invoice_number)
            main_window.tabs.widget(1).subject.setText("RFQ - TRW " + invoice_number)
        except Exception as e:
            sendMessage("Copy Quote",str(e),self)

class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stylesheets/Settings Stylesheet.css")
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.UIComponents()

    def UIComponents(self):
        try:
            self.tool_box = QToolBox()

            #STYLE
            self.style_group = QGroupBox()
            self.style_group.setCheckable(False)
            self.style_layout = QVBoxLayout()
            self.style_group.setLayout(self.style_layout)

            for theme in ("Dark, Orange","Dark, Blue","Classic","Dark","Light"):
                btn = QRadioButton(theme)
                btn.clicked.connect(lambda: self.change_style())
                if THEME == theme:
                    btn.setChecked(True)
                self.style_layout.addWidget(btn)

            button_group = QButtonGroup()
            button_group.setExclusive(True)

            #Item table boxes - Done Later

            #DATABASE HEADERS & SEARCHES
            database_widget = self.getDatabaseWid()

            ##USERS, PARTS, CONDITIONS
            user_widget = self.getUserStockCondWid()

            ##LINKED FILES
            linked_widget = self.getLinkedFilesWid()


            #SETUP TOOLBOX AND MAIN LAYOUT FOR TAB
            self.tool_box.addItem(self.style_group,"Style")
            self.tool_box.addItem(self.refresh_table_maker(),"Item Table")
            self.tool_box.addItem(database_widget,"Database")
            self.tool_box.addItem(user_widget,"Quote Settings")
            self.tool_box.addItem(linked_widget,"Linked Files")
            self.tool_box.addItem(QWidget(),"")
            self.tool_box.setContentsMargins(80,80,100,100)

            self.tool_box.setCurrentIndex(self.tool_box.count()-1)

            self.main_layout = QVBoxLayout()
            self.main_layout.addWidget(self.tool_box)
            self.setLayout(self.main_layout)
        except Exception as e:
            sendMessage("Settings GUI Setup", str(e), self)

    def getLinkedFilesWid(self):
        global shared_settings_file
        ##Database
        self.database_list = QListWidget()

        for file in STORED_DATABASE_PATHS:
            self.database_list.addItem(QListWidgetItem(file, self.database_list))

        del_database = QPushButton("Delete")
        del_database.setObjectName("with-list")
        del_database.clicked.connect(self.delDatabase)

        self.new_database = QLineEdit()
        self.new_database.setPlaceholderText("Database Path")
        self.new_database.setObjectName("with-list")

        browse = QPushButton("Browse")
        browse.clicked.connect(self.browseDatabase)
        browse.setObjectName("with-list")

        submit_data = QPushButton("Submit")
        submit_data.clicked.connect(self.addDatabase)
        submit_data.setObjectName("with-list")

        data_btn_lay = QVBoxLayout()
        # data_btn_lay.setAlignment(QtCore.Qt.AlignCenter)
        data_btn_lay.setSpacing(10)
        data_btn_lay.addWidget(self.new_database)
        data_btn_lay.addWidget(browse)
        data_btn_lay.addWidget(submit_data)
        data_btn_lay.addWidget(del_database)

        data_lay = QHBoxLayout()
        data_lay.addWidget(self.database_list)
        data_lay.addLayout(data_btn_lay)

        use_database = QPushButton("Select Database")
        use_database.clicked.connect(self.useDatabase)
        use_database.setObjectName("with-list")

        save_database = QPushButton("Save")
        save_database.clicked.connect(self.saveDatabase)
        save_database.setObjectName("with-list")

        #Layout for database and it's button
        database_lay = QVBoxLayout()
        database_lay.setAlignment(QtCore.Qt.AlignCenter)
        database_lay.addLayout(data_lay)
        database_lay.addWidget(use_database)
        #lay.addWidget(save_database) used to be button to save databse file path

        ##SHARED SETTINGS
        self.shared_settings_lay = SettingsList([shared_settings_file],"Shared Settings File",True,"Pickle","(*.pickle)")

        save_shared_file = QPushButton("Use Shared File")
        save_shared_file.clicked.connect(self.save_shared_settings)
        save_shared_file.setObjectName("with-list")

        file_lay = QVBoxLayout()
        file_lay.setAlignment(QtCore.Qt.AlignCenter)
        file_lay.addLayout(self.shared_settings_lay)
        file_lay.addWidget(save_shared_file)

        ##MAIN LAYOUT
        main_lay = QVBoxLayout()
        main_lay.setAlignment(QtCore.Qt.AlignCenter)
        main_lay.addLayout(data_lay)
        main_lay.addLayout(database_lay)
        main_lay.addLayout(file_lay)
        #main_lay.addLayout(shared_settings_lay)
        #database_lay.addLayout(lay)

        data_widget = QWidget()
        data_widget.setLayout(main_lay)

        return data_widget

    def getDatabaseWid(self):
        try:
            #Database Headers
            self.database_edit_layout = QHBoxLayout()
            for header in database_headers:
                self.addCol(header)

            self.database_btn_layout = QHBoxLayout()
            self.database_submit_btn = QPushButton("Submit")
            self.database_submit_btn.clicked.connect(lambda: self.submitHeaders())
            self.database_add_col_btn = QPushButton("Add Header")
            self.database_add_col_btn.clicked.connect(lambda: self.addCol(preferred_search))
            self.database_del_col_btn = QPushButton("Delete Header")
            self.database_del_col_btn.clicked.connect(lambda: self.delCol())
            for btn in (self.database_submit_btn, self.database_add_col_btn, self.database_del_col_btn):
                self.database_btn_layout.addWidget(btn)
                btn.setObjectName("database-edit")

            head_lay = QVBoxLayout()
            head_lay.addLayout(self.database_edit_layout)
            head_lay.addLayout(self.database_btn_layout)

            header_group = QGroupBox("Headers")
            header_group.setAlignment(QtCore.Qt.AlignCenter)
            header_group.setLayout(head_lay)

            #Database Search Boxes
            self.search1 = QComboBox()
            self.search2 = QComboBox()
            self.search3 = QComboBox()

            save_searches = QPushButton("Save")
            save_searches.clicked.connect(self.saveSearchBy)
            save_searches.setMaximumSize(120,30)

            lay = QHBoxLayout()
            for wid in (self.search1,self.search2,self.search3):
                self.addComboOptions(wid)
                wid.setObjectName("search")
                lay.addWidget(wid)

            vlay = QVBoxLayout()
            vlay.addLayout(lay)
            vlay.addWidget(save_searches)

            self.search1.setCurrentText(DATABASE_SEARCHES[0].replace("_"," "))
            self.search2.setCurrentText(DATABASE_SEARCHES[1].replace("_"," "))
            self.search3.setCurrentText(DATABASE_SEARCHES[2].replace("_"," "))

            search_group = QGroupBox("Search Functions")
            search_group.setAlignment(QtCore.Qt.AlignCenter)
            search_group.setLayout(vlay)

            self.database_layout = QVBoxLayout()
            self.database_layout.addWidget(header_group)
            self.database_layout.addWidget(search_group)
            database_widget = QWidget()
            database_widget.setLayout(self.database_layout)

            return database_widget
        except Exception as e:
            sendMessage("Get Database Wid",str(e),self)

    def saveSearchBy(self): #TODO: Make sure actually works, change _Date to __Date
        try:
            DATABASE_SEARCHES.clear()
            DATABASE_SEARCHES.append(self.search1.currentText().replace(" ","_"))
            DATABASE_SEARCHES.append(self.search2.currentText().replace(" ", "_"))
            DATABASE_SEARCHES.append(self.search3.currentText().replace(" ", "_"))

            storeSettings()

            main_window.tabs.widget(0).search1.setPlaceholderText("Search by " + DATABASE_SEARCHES[0].replace("_", " "))
            main_window.tabs.widget(0).search2.setPlaceholderText("Search by " + DATABASE_SEARCHES[1].replace("_", " "))
            main_window.tabs.widget(0).search3.setPlaceholderText("Search by " + DATABASE_SEARCHES[2].replace("_", " "))
        except Exception as e:
            sendMessage("Save SearchBy",str(e),self)

    def addComboOptions(self, box):
        try:
            self.search_dictionary = {}
            #for search in database_headers: #only specific few
            for search in DATABASE_HEADERS: #So can choose from all database headers
                #self.search_dictionary["Search by " + search.replace("_"," ")] = search.replace(" ","_") #used to be search.lower for the key
                if "Date" not in search:
                    self.search_dictionary[search.replace("_"," ")] = search.replace(" ","_")
                # self.search_by_box.addItem("Search by "+search.lower())
            box.addItems(self.search_dictionary.keys())

            for i in range(box.count()):
                if preferred_search.lower() in box.itemText(i).lower():
                    box.setCurrentText(box.itemText(i))
        except Exception as e:
            sendMessage("Database Add Combo Options", str(e), self)

    def getUserStockCondWid(self):
        try:
            # USERS/PART CONDITIONS/STOCK

            # Users
            self.user_list = QListWidget()
            for user in senders:
                self.addUser(user, senders[user])

            self.user_name = QLineEdit()
            self.user_name.setPlaceholderText("User Name")
            self.user_name.setObjectName("with-list")

            self.user_email = QLineEdit()
            self.user_email.setPlaceholderText("User Email")
            self.user_email.setObjectName("with-list")

            submit_user = QPushButton("Submit")
            submit_user.clicked.connect(self.submitUser)
            submit_user.setObjectName("with-list")

            del_user = QPushButton("Delete")
            del_user.clicked.connect(self.deleteUser)
            del_user.setObjectName("with-list")

            submit_layout = QVBoxLayout()
            submit_layout.addWidget(self.user_name)
            submit_layout.addWidget(self.user_email)
            submit_layout.addWidget(submit_user)
            submit_layout.addWidget(del_user)

            user_layout = QHBoxLayout()
            user_layout.addWidget(self.user_list)
            user_layout.addLayout(submit_layout)

            # Part Conditions
            self.conditions_list = QListWidget()
            for condition in part_conditions:
                self.conditions_list.addItem(QListWidgetItem(condition))

            self.condition = QLineEdit()
            self.condition.setPlaceholderText("Condition")
            self.condition.setObjectName("with-list")

            submit_condition = QPushButton("Submit")
            submit_condition.clicked.connect(self.submitCondition)
            submit_condition.setObjectName("with-list")

            del_condition = QPushButton("Delete")
            del_condition.clicked.connect(self.deleteCondition)
            del_condition.setObjectName("with-list")

            condition_up = QToolButton()
            condition_up.setArrowType(QtCore.Qt.UpArrow)
            condition_up.clicked.connect(lambda: self.conditionUp())

            condition_down = QToolButton()
            condition_down.setArrowType(QtCore.Qt.DownArrow)
            condition_down.clicked.connect(lambda: self.conditionDown())

            condition_upup = QToolButton()
            condition_upup.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double up arrow.png")))
            condition_upup.clicked.connect(lambda: self.conditionUp(True))

            condition_dndn = QToolButton()
            condition_dndn.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double down arrow.png")))
            condition_dndn.clicked.connect(lambda: self.conditionDown(True))

            cond_grid = QGridLayout()
            cond_grid.addWidget(submit_condition, 0, 0)
            cond_grid.addWidget(del_condition, 1, 0)
            cond_grid.addWidget(condition_up, 0, 1)
            cond_grid.addWidget(condition_upup, 0, 2)
            cond_grid.addWidget(condition_down, 1, 1)
            cond_grid.addWidget(condition_dndn, 1, 2)

            sub_layout = QVBoxLayout()
            sub_layout.addWidget(self.condition)
            sub_layout.addLayout(cond_grid)
            # sub_layout.addWidget(submit_condition)
            # sub_layout.addWidget(del_condition)

            condition_layout = QHBoxLayout()
            condition_layout.addWidget(self.conditions_list)
            condition_layout.addLayout(sub_layout)

            # STOCK
            self.stock_list = QListWidget()
            for stock in stock_options:
                self.stock_list.addItem(QListWidgetItem(stock))

            self.stock = QLineEdit()
            self.stock.setPlaceholderText("Stock")
            self.stock.setObjectName("with-list")

            submit_stock = QPushButton("Submit")
            submit_stock.clicked.connect(self.submitStock)
            submit_stock.setObjectName("with-list")

            del_stock = QPushButton("Delete")
            del_stock.clicked.connect(self.deleteStock)
            del_stock.setObjectName("with-list")

            stock_up = QToolButton()
            stock_up.setArrowType(QtCore.Qt.UpArrow)
            stock_up.clicked.connect(lambda: self.stockUp())

            stock_down = QToolButton()
            stock_down.setArrowType(QtCore.Qt.DownArrow)
            stock_down.clicked.connect(lambda: self.stockDown())

            stock_upup = QToolButton()
            stock_upup.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double up arrow.png")))
            stock_upup.clicked.connect(lambda: self.stockUp(True))

            stock_dndn = QToolButton()
            stock_dndn.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double down arrow.png")))
            stock_dndn.clicked.connect(lambda: self.stockDown(True))

            stockrow1 = QHBoxLayout()
            stockrow1.addWidget(submit_stock)
            stockrow1.addWidget(stock_up)
            stockrow1.addWidget(stock_upup)

            stockrow2 = QHBoxLayout()
            stockrow2.addWidget(del_stock)
            stockrow2.addWidget(stock_down)
            stockrow2.addWidget(stock_dndn)

            sub_lay = QVBoxLayout()
            sub_lay.addWidget(self.stock)
            sub_lay.addLayout(stockrow1)
            sub_lay.addLayout(stockrow2)
            # sub_lay.addWidget(submit_stock)
            # sub_lay.addWidget(del_stock)

            stock_layout = QHBoxLayout()
            stock_layout.addWidget(self.stock_list)
            stock_layout.addLayout(sub_lay)

            #NOTE CHECKBUTTONS
            self.notes_list = QListWidget()
            for note in sample_notes:
                self.notes_list.addItem(QListWidgetItem(note))

            self.note = QLineEdit()
            self.note.setPlaceholderText("Note")
            self.note.setObjectName("with-list")

            submit_note = QPushButton("Submit")
            submit_note.clicked.connect(self.submitNote)
            submit_note.setObjectName("with-list")

            del_note = QPushButton("Delete")
            del_note.clicked.connect(self.deleteNote)
            del_note.setObjectName("with-list")

            note_up = QToolButton()
            note_up.setArrowType(QtCore.Qt.UpArrow)
            note_up.clicked.connect(lambda: self.moveListItemUp(self.notes_list))

            note_down = QToolButton()
            note_down.setArrowType(QtCore.Qt.DownArrow)
            note_down.clicked.connect(lambda: self.moveListItemDown(self.notes_list))

            note_upup = QToolButton()
            note_upup.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double up arrow.png")))
            note_upup.clicked.connect(lambda: self.moveListItemUp(self.notes_list,True))

            note_dndn = QToolButton()
            note_dndn.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double down arrow.png")))
            note_dndn.clicked.connect(lambda: self.moveListItemDown(self.notes_list,True))

            note_grid = QGridLayout()
            note_grid.addWidget(submit_note,0,0)
            note_grid.addWidget(del_note,1,0)
            note_grid.addWidget(note_up,0,1)
            note_grid.addWidget(note_upup,0,2)
            note_grid.addWidget(note_down,1,1)
            note_grid.addWidget(note_dndn,1,2)

            note_side_lay = QVBoxLayout()
            note_side_lay.addWidget(self.note)
            note_side_lay.addLayout(note_grid)

            note_h_lay = QHBoxLayout()
            note_h_lay.addWidget(self.notes_list)
            note_h_lay.addLayout(note_side_lay)

            #PAYMENT TERMS
            self.payment_list = QListWidget()
            for pay in PAYMENT_TERMS:
                self.payment_list.addItem(QListWidgetItem(pay))

            self.payment = QLineEdit()
            self.payment.setPlaceholderText("Payment Term")
            self.payment.setObjectName("with-list")

            submit_payment = QPushButton("Submit")
            submit_payment.clicked.connect(self.submitPayment)
            submit_payment.setObjectName("with-list")

            del_payment = QPushButton("Delete")
            del_payment.clicked.connect(self.deletePayment)
            del_payment.setObjectName("with-list")

            payment_up = QToolButton()
            payment_up.setArrowType(QtCore.Qt.UpArrow)
            payment_up.clicked.connect(lambda: self.moveListItemUp(self.payment_list))

            payment_down = QToolButton()
            payment_down.setArrowType(QtCore.Qt.DownArrow)
            payment_down.clicked.connect(lambda: self.moveListItemDown(self.payment_list))

            payment_upup = QToolButton()
            payment_upup.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double up arrow.png")))
            payment_upup.clicked.connect(lambda: self.moveListItemUp(self.payment_list, True))

            payment_dndn = QToolButton()
            payment_dndn.setIcon(
                QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images/double down arrow.png")))
            payment_dndn.clicked.connect(lambda: self.moveListItemDown(self.payment_list, True))

            payment_grid = QGridLayout()
            payment_grid.addWidget(submit_payment, 0, 0)
            payment_grid.addWidget(del_payment, 1, 0)
            payment_grid.addWidget(payment_up, 0, 1)
            payment_grid.addWidget(payment_upup, 0, 2)
            payment_grid.addWidget(payment_down, 1, 1)
            payment_grid.addWidget(payment_dndn, 1, 2)

            payment_side_lay = QVBoxLayout()
            payment_side_lay.addWidget(self.payment)
            payment_side_lay.addLayout(payment_grid)

            payment_h_lay = QHBoxLayout()
            payment_h_lay.addWidget(self.payment_list)
            payment_h_lay.addLayout(payment_side_lay)

            #Submit/Cancel Buttons
            save_userPartStock = QPushButton("Save")
            save_userPartStock.clicked.connect(self.saveUsersStockConditions)
            save_userPartStock.setObjectName("with-list")

            cancel_userPartStock = QPushButton("Cancel")
            cancel_userPartStock.clicked.connect(self.cancelUsersStockConditions)
            cancel_userPartStock.setObjectName("with-list")

            USC_submit_lay = QHBoxLayout()
            USC_submit_lay.addWidget(save_userPartStock)
            USC_submit_lay.addWidget(cancel_userPartStock)

            # setup user/part condition/stock layout and widget
            userPartStock_layout = QVBoxLayout()
            userPartStock_layout.addLayout(user_layout)
            userPartStock_layout.addLayout(condition_layout)
            userPartStock_layout.addLayout(stock_layout)
            userPartStock_layout.addLayout(note_h_lay)
            userPartStock_layout.addLayout(payment_h_lay)
            userPartStock_layout.addLayout(USC_submit_lay)
            # userPartStock_layout.addWidget(save_userPartStock)

            user_widget = QWidget()
            user_widget.setLayout(userPartStock_layout)

            return user_widget
        except Exception as e:
            sendMessage("User Part Cond",str(e),self)

    def updateUserStockCondWid(self):
        self.conditions_list.clear()
        #for condition in part_conditions:
            #self.conditions_list.addItem(QListWidgetItem(condition))
        self.conditions_list.addItem(QListWidgetItem("YOLLO"))

        self.stock_list.clear()
        for stock in stock_options:
            self.stock_list.addItem(QListWidgetItem(stock))

        self.user_list.clear()
        for user in senders:
            self.addUser(user, senders[user])


    def refresh_table_maker(self,delete_tab = False):
        try:
            self.table_splitter = QSplitter()
            self.table_splitter.setOrientation(QtCore.Qt.Horizontal)
            for header in table_headers:
                edit = QLineEdit(header)
                edit.setAlignment(QtCore.Qt.AlignCenter)
                self.table_splitter.addWidget(edit)

            self.table_submit_layer = QHBoxLayout()
            self.table_submit_btn = QPushButton("Submit")
            self.table_refresh_btn = QPushButton("Refresh")
            self.table_refresh_btn.clicked.connect(lambda: self.refresh_table_maker(delete_tab=True))
            self.table_add_btn = QPushButton("Add Column")
            self.table_delete_btn = QPushButton("Delete Column")

            for btn in (self.table_submit_btn,self.table_refresh_btn,self.table_add_btn,self.table_delete_btn):
                self.table_submit_layer.addWidget(btn)
                btn.setObjectName("submit")

            self.table_layout = QVBoxLayout()
            self.table_layout.addWidget(self.table_splitter)
            self.table_layout.addLayout(self.table_submit_layer)
            widget = QWidget()
            widget.setLayout(self.table_layout)

            if delete_tab:
                index = self.tool_box.currentIndex()
                self.tool_box.removeItem(index)
                self.tool_box.insertItem(index,widget,"Item Table")
                self.tool_box.setCurrentIndex(index)
            else:
                return widget
        except Exception as e:
            print(e)

    def change_style(self):
        try:
            global Alternating_color,Alternating_font, ALTERNATING_COLORS #TODO: Fix already alternated rows if switch Themes

            btn = self.sender()
            text = btn.text()

            setTheme(text)

            storeSettings()
            #refresh()

        except Exception as e:
            print(e,535)

    def submitHeaders(self):
        #TODO: Possibly select which one want to delete? how select two objects at once
        try:
            global database_headers

            for i in range(len(database_headers)):
                database_headers.pop()

            for i in range(self.database_edit_layout.count()):
                database_headers.append(self.database_edit_layout.itemAt(i).widget().currentText())
            storeSettings()
        except Exception as e:
            sendMessage("Settings Submit Headers",str(e),self)

    def addCol(self,header):
        wid = QComboBox()
        wid.addItems(DATABASE_HEADERS)
        wid.setCurrentText(header.replace(" ","_"))
        wid.setObjectName("database-header")
        self.database_edit_layout.addWidget(wid)

    def delCol(self):
        length = self.database_edit_layout.count()-1
        if length > 0:
            wid = self.database_edit_layout.itemAt(length).widget()
            self.database_edit_layout.removeWidget(wid)

    #add user to user_list
    def addUser(self,name,email):
        try:
            self.user_list.addItem(QListWidgetItem(name+": "+email,self.user_list))
        except Exception as e:
            print(e)

    def deleteUser(self):
        try:
            selected_items = self.user_list.selectedItems()
            user_info = []

            for item in selected_items:
                user_info.append(item.text())
                self.user_list.takeItem(self.user_list.row(item))

            #for info in user_info:
                #name, email = self.splitUserInfo(info)
                #senders.pop(name)

        except Exception as e:
            print(e)

    def submitUser(self):
        try:
            name = self.user_name.text()
            if name != "":
                self.user_name.clear()
                email = self.user_email.text()
                self.user_email.clear()

                #insert into list
                self.addUser(name,email)

            #add to senders dictionary
            #senders[name] = email
            #storeSettings()
        except Exception as e:
            print(e)

    def splitUserInfo(self,info):
        name = ""
        email = ""

        for s in info:
            if s != ":":
                name += s
                info = info[1:]
            else:
                break
        #remove space
        info = info[1:]

        email = info

        return name, email

    def submitCondition(self):
        try:
            condition = self.condition.text()
            if condition != "":
                self.condition.clear()
                self.conditions_list.addItem(QListWidgetItem(condition))

            #part_conditions.append(condition)
            #storeSettings()
        except Exception as e:
            print(e)

    def deleteCondition(self):
        try:
            selected_items = self.conditions_list.selectedItems()

            for item in selected_items:
                self.conditions_list.takeItem(self.conditions_list.row(item))
                #part_conditions.remove(item.text())

        except Exception as e:
            print(e)

    def conditionUp(self,first=False):
        try:
            row = self.conditions_list.currentRow()
            item = self.conditions_list.takeItem(row)

            if first:
                row = 0
            else:
                row -= 1

            self.conditions_list.insertItem(row, item)
            self.conditions_list.setCurrentRow(row)
        except Exception as e:
            sendMessage("Move Up",str(e),self)

    def conditionDown(self,last=False):
        try:
            row = self.conditions_list.currentRow()
            item = self.conditions_list.takeItem(row)

            if last:
                row = self.conditions_list.count()
            else:
                row += 1

            self.conditions_list.insertItem(row, item)
            self.conditions_list.setCurrentRow(row)
        except Exception as e:
            sendMessage("Move Down",str(e),self)

    def submitStock(self):
        try:
            stock = self.stock.text()
            if stock != "":
                self.stock.clear()
                self.stock_list.addItem(QListWidgetItem(stock))

            #stock_options.append(stock)
            #storeSettings()
        except Exception as e:
            print(e)

    def deleteStock(self):
        try:
            selected_items = self.stock_list.selectedItems()

            for item in selected_items:
                self.stock_list.takeItem(self.stock_list.row(item))
                #stock_options.remove(item.text())

        except Exception as e:
            print(e)

    def stockUp(self,first=False):
        try:
            row = self.stock_list.currentRow()
            item = self.stock_list.takeItem(row)

            if first:
                row = 0
            else:
                row -= 1

            self.stock_list.insertItem(row, item)
            self.stock_list.setCurrentRow(row)
        except Exception as e:
            sendMessage("Move Up",str(e),self)

    def stockDown(self,last=False):
        try:
            row = self.stock_list.currentRow()
            item = self.stock_list.takeItem(row)

            if last:
                row = self.stock_list.count()
            else:
                row += 1

            self.stock_list.insertItem(row, item)
            self.stock_list.setCurrentRow(row)
        except Exception as e:
            sendMessage("Move Down",str(e),self)

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
            sendMessage("Move Down",str(e),self)

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
            sendMessage("Move Down",str(e),self)

    def submitNote(self):
        try:
            note = self.note.text()
            if note != "":
                self.note.clear()
                self.notes_list.addItem(QListWidgetItem(note))

            #stock_options.append(stock)
            #storeSettings()
        except Exception as e:
            sendMessage("Submit Note",str(e),self)

    def deleteNote(self):
        try:
            selected_items = self.notes_list.selectedItems()

            for item in selected_items:
                self.notes_list.takeItem(self.notes_list.row(item))
                #stock_options.remove(item.text())

        except Exception as e:
            sendMessage("Submit Note",str(e),self)

    def submitPayment(self):
        try:
            payment = self.payment.text()
            if payment != "":
                self.payment.clear()
                self.payment_list.addItem(QListWidgetItem(payment))

            #stock_options.append(stock)
            #storeSettings()
        except Exception as e:
            sendMessage("Submit Payment",str(e),self)

    def deletePayment(self):
        try:
            selected_items = self.payment_list.selectedItems()

            for item in selected_items:
                self.payment_list.takeItem(self.payment_list.row(item))
                #stock_options.remove(item.text())

        except Exception as e:
            sendMessage("Submit Payment",str(e),self)

    def cancelUsersStockConditions(self):
        self.tool_box.removeItem(3)
        user_widget = self.getUserStockCondWid()
        self.tool_box.insertItem(3,user_widget, "Quote Settings")
        self.tool_box.setCurrentIndex(3)

    def saveUsersStockConditions(self):
        try:
            global senders, part_conditions,stock_options,sample_notes,PAYMENT_TERMS

            users = {}
            for i in range(self.user_list.count()):
                name,email = self.splitUserInfo(self.user_list.item(i).text())
                users[name] = email

            conditions = []
            for i in range(self.conditions_list.count()):
                conditions.append(self.conditions_list.item(i).text())

            stock = []
            for i in range(self.stock_list.count()):
                stock.append(self.stock_list.item(i).text())

            notes = []
            for i in range(self.notes_list.count()):
                notes.append(self.notes_list.item(i).text())

            payments = []
            for i in range(self.payment_list.count()):
                payments.append(self.payment_list.item(i).text())

            #STORE SETTINGS

            senders.clear()
            for user in users:
                senders[user] = users[user]
            #senders = users

            part_conditions.clear()
            part_conditions = conditions

            stock_options.clear()
            stock_options = stock

            sample_notes.clear()
            sample_notes = notes

            PAYMENT_TERMS.clear()
            PAYMENT_TERMS = payments

            storeSettings()

            sendMessage("Settings Saved","Quote Settings have been successfully saved",self,QMessageBox.Information)

        except Exception as e:
            print(e)

    def delDatabase(self):
        try:
            selected_items = self.database_list.selectedItems()

            for item in selected_items:
                self.database_list.takeItem(self.database_list.row(item))
        except Exception as e:
            sendMessage("Delete Database Path",str(e),self)

    def addDatabase(self):
        try:
            database = self.new_database.text()
            self.new_database.clear()
            self.database_list.addItem(QListWidgetItem(database))
        except Exception as e:
            sendMessage("Add Database Path", str(e), self)

    def browseDatabase(self):
        try:
            database_path = QFileDialog.getOpenFileName(self, "Open database",
                                                        os.path.join(os.path.expanduser("~"), "Documents"),
                                                        'Microsoft Access (*.accdb)')
            self.new_database.setText(str(database_path[0]))
        except Exception as e:
            print(e)

    #Selects new database to pull from
    def useDatabase(self):
        global database_file,STORED_DATABASE_PATHS
        try:
            selected_items = self.database_list.selectedItems()

            for item in selected_items:
                closeDatabaseConnection() #Close old connection
                connectDatabase(item.text())
                sendMessage("New Database Connection",item.text()+" is the new database",self)

            self.saveDatabase()

            #Store database
            STORED_DATABASE_PATHS.clear()

            for i in range(self.database_list.count()):
                STORED_DATABASE_PATHS.append(self.database_list.item(i).text())

            storeDatabase(database_file)

        except Exception as e:
            sendMessage("Connect New Database",str(e),self)
            connectDatabase(database_file)

    def saveDatabase(self): #NOT USED -
        try:
            global STORED_DATABASE_PATHS,database_file

            STORED_DATABASE_PATHS.clear()

            for i in range(self.database_list.count()):
                STORED_DATABASE_PATHS.append(self.database_list.item(i).text())

            storeDatabase(database_file)
        except Exception as e:
            sendMessage("Save Database", str(e), self)
            #raise Exception - for when hit "select databse function", will stop that loop as well, but doesn't work for just the "save" button

    def save_shared_settings(self):
        try:
            global shared_settings_file

            selected_items = self.shared_settings_lay.list.selectedItems()
            for item in selected_items:
                file = item.text()
                if file == None or file == "None":
                    sendMessage("No file selected","Please select a file to use", self)
                    return False

            shared_settings_file = file

            storeSettings(shared=False)
            errors = []
            loadSharedVariables(errors)
            for li in errors:
                sendMessage(li[0], str(li[1]), main_window)

            sendMessage("New Database Connection", file + " is the new shared file", self)
            #Refresh tab so new ones show
            main_window.tabs.removeTab(3)
            main_window.tabs.insertTab(3,Settings(), "Settings")
            main_window.tabs.setCurrentIndex(3)
            set_settings_tab(3)
        except Exception as e:
            sendMessage("Save Shared File", str(e), self)

def set_settings_tab(p_int):
    main_window.tabs.widget(4).tool_box.setCurrentIndex(p_int)

class Database(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stylesheets/Database Stylesheet.css")
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.sorted_by = ["",""]
        self.MAX_LISTINGS = 25
        self.listing_index = 0
        self.last_click = "L"

        self.UIComponents()

    def UIComponents(self):
        try:
            self.new_quote_btn = QPushButton("New Quote")
            self.new_quote_btn.clicked.connect(lambda: self.newQuote())

            self.refresh_btn = QPushButton("Refresh")
            self.refresh_btn.clicked.connect(self.onSubmitSearch)

            self.search1 = QLineEdit()
            self.search1.setPlaceholderText("Search by "+DATABASE_SEARCHES[0].replace("_"," "))
            self.search2 = QLineEdit()
            self.search2.setPlaceholderText("Search by "+DATABASE_SEARCHES[1].replace("_"," "))
            self.search3 = QLineEdit()
            self.search3.setPlaceholderText("Search by "+DATABASE_SEARCHES[2].replace("_"," "))

            for wid in (self.search1,self.search2,self.search3):
                wid.setObjectName("search")
                wid.returnPressed.connect(self.onSubmitSearch)
                wid.setAlignment(QtCore.Qt.AlignCenter)

            self.search_btn = QPushButton(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),"images/search image.png")),"Search")
            self.search_btn.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.search_btn.clicked.connect(self.onSubmitSearch)

            self.max_listings_box = QComboBox()
            self.max_listings_box.setObjectName("listings")
            self.max_listings_box.setEditable(False)
            self.max_listings_box.addItems(['10','25','50','100'])
            self.max_listings_box.setCurrentText(str(self.MAX_LISTINGS))
            self.max_listings_box.currentIndexChanged.connect(self.changeListings)

            listings_label = QLabel("Entries: ")
            listings_label.setMaximumWidth(40)

            listings_lay = QHBoxLayout()
            listings_lay.setSpacing(0)
            listings_lay.addWidget(listings_label)
            listings_lay.addWidget(self.max_listings_box)

            self.search_layer = QHBoxLayout()
            self.search_layer.addLayout(listings_lay)
            for wid in (self.new_quote_btn,self.refresh_btn,self.search1,self.search2,self.search3,self.search_btn):
                self.search_layer.addWidget(wid)
                wid.setObjectName("search")
            self.search_layer.setAlignment(QtCore.Qt.AlignRight)

            self.table_grid = QGridLayout()
            self.table_grid.setSpacing(0)
            self.table_grid.setVerticalSpacing(0)
            self.table_grid.setSizeConstraint(QLayout.SetMinimumSize)
            self.addTableHeaders()

            self.left = QToolButton()
            self.left.setArrowType(QtCore.Qt.LeftArrow)
            self.left.clicked.connect(self.moveSearchLeft)
            self.right = QToolButton()
            self.right.setArrowType(QtCore.Qt.RightArrow)
            self.right.clicked.connect(self.moveSearchRight)

            arrow_lay = QHBoxLayout()
            arrow_lay.addWidget(self.left)
            arrow_lay.addWidget(self.right)
            arrow_lay.setAlignment(QtCore.Qt.AlignCenter)

            search_lay = QVBoxLayout()
            search_lay.addLayout(self.table_grid)
            search_lay.addLayout(arrow_lay)
            search_lay.setSpacing(0)

            self.main_layout = QVBoxLayout()
            self.main_layout.addLayout(self.search_layer)
            self.main_layout.addLayout(search_lay)
            self.main_layout.setSpacing(50)

            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            wid = QWidget()
            wid.setLayout(self.main_layout)
            self.scroll_area.setWidget(wid)
            lay = QVBoxLayout()
            lay.addWidget(self.scroll_area)
            self.setLayout(lay)
        except Exception as e:
            sendMessage("Database GUI Setup", str(e), self)

    def addComboOptions(self, box):
        try:
            self.search_dictionary = {}
            #for search in database_headers: #only specific few
            for search in DATABASE_HEADERS: #So can choose from all database headers
                self.search_dictionary["Search by " + search.replace("_"," ")] = search.replace(" ","_") #used to be search.lower for the key
                # self.search_by_box.addItem("Search by "+search.lower())
            box.addItems(self.search_dictionary.keys())

            for i in range(box.count()):
                if preferred_search.lower() in box.itemText(i).lower():
                    box.setCurrentText(box.itemText(i))
        except Exception as e:
            sendMessage("Database Add Combo Options", str(e), self)

    def changeListings(self):
        try:
            combo = self.sender()
            self.MAX_LISTINGS = int(combo.currentText())

            self.firstSearchInput()

        except Exception as e:
            sendMessage("Database changeListings", str(e), self)

    def firstSearchInput(self):
        self.listing_index = 0
        self.last_click = "L"

        df = pandas.DataFrame()
        self.index = self.listing_index + self.MAX_LISTINGS
        for i in range(self.listing_index, self.index):
            if i > len(self.searched_df) - 1:  # For if still some rows left, but under MAX_LISTINGS
                break
            df = df.append(self.searched_df.iloc[i], ignore_index=True)
        self.insertDatabaseGrid(df)

    def moveSearchRight(self):
        try:
            df = pandas.DataFrame()
            if self.last_click == "L" and (self.listing_index + self.MAX_LISTINGS) < len(self.searched_df):
                self.listing_index = self.index
            self.index = self.listing_index + self.MAX_LISTINGS

            if self.listing_index - 1 < len(self.searched_df)-1: #When no more listings, don't even try to change
                for i in range(self.listing_index,self.index):
                    if i > len(self.searched_df)-1: #For if still some rows left, but under MAX_LISTINGS
                        break
                    df = df.append(self.searched_df.iloc[i],ignore_index=True)
                self.insertDatabaseGrid(df)
                self.last_click = "L"
        except Exception as e:
            print(e)
    def moveSearchLeft(self):
        try:
            df = pandas.DataFrame()
            if self.last_click == "R" and (self.index - self.MAX_LISTINGS) > -1:
                self.listing_index = self.index
            self.index = self.listing_index - self.MAX_LISTINGS

            if self.listing_index > 0:  # When no more listings, don't even try to change
                for i in reversed(range(self.index,self.listing_index)):
                    if i < 0:  # For if still some rows left, but under MAX_LISTINGS
                        break
                    df = df.append(self.searched_df.iloc[i], ignore_index=True)

                df = df.iloc[::-1] #re-reversed it so still sorted correctly
                self.insertDatabaseGrid(df)
                self.last_click = "R"
        except Exception as e:
            print(e)

    def submit_search_keep_place(self):
        try:
            listing_index = self.listing_index

            # Resubmit search so table updates
            self.onSubmitSearch()

            # puts database where used to be
            while (listing_index > self.listing_index):
                self.moveSearchRight()
        except Exception as e:
            sendMessage("Submit Search Keep Place",str(e),self)

    def onSubmitSearch(self):
        try:
            search_by1 = DATABASE_SEARCHES[0]
            search_by2 = DATABASE_SEARCHES[1]
            search_by3 = DATABASE_SEARCHES[2]

            search1 = self.search1.text()
            search2 = self.search2.text()
            search3 = self.search3.text()

            searched_df = getQuotes3(search1, search2, search3, search_by1, search_by2, search_by3)

            self.searched_df = searched_df.sort_values("Quote_Number", ascending=False)
            self.sorted_by[0] = "Quote_Number"
            self.sorted_by[1] = False

            # ADD ROWS INTO TABLE
            self.firstSearchInput()
        except Exception as e:
            sendMessage("Submit Search",str(e),self)

    def insertDatabaseGrid(self,df):
        try:
            # DELETE GRID AND CREATE NEW ONE - JUST TO PREVENT MISHMASH IF CONSTANTLY DELETING WIDGETS
            if self.table_grid is not None:
                while self.table_grid.count():
                    item = self.table_grid.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            self.addTableHeaders()
            # self.main_layout.addLayout(self.table_grid)

            large_rows = []

            for i in range(len(df)): #Rows in df
                for j in range(len(database_headers)): #Col in grid
                    widget = ClickableLineEdit(str(df[(database_headers[j]).replace(" ", "_")].values[i]).replace(";", ", "))
                    #widget.setStyleSheet("color: white;")
                    maxwidth = QFontMetrics(widget.font()).maxWidth()
                    textlen = len(widget.text())
                    if textlen > (widget.width()/maxwidth): #if too long for single line, move to double line qlabel
                        #widget = QLabel(str(df[(database_headers[j]).replace(" ", "_")].values[i]).replace(";", ", "))
                        widget = ClickableLabel(str(df[(database_headers[j]).replace(" ", "_")].values[i]).replace(";", ", "))
                        widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        widget.setWordWrap(True)
                        if i not in large_rows:
                            large_rows.append(i)
                        #widget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding)
                    ##if j == 0: #allows quote number to be clicked to view quote
                        #widget = ClickableLineEdit(str(df[(database_headers[j]).replace(" ","_")].values[i]).replace(";",", "))
                        ##widget.clicked.connect(self.viewQuote)
                        ##widget.setObjectName("database-click")
                        ##if i % 2 == 0:  # Alternate row colors
                            ##widget.setStyleSheet("QLineEdit{background: " + Alternating_color + "; color: " + Alternating_font + ";}QLineEdit::hover{color:blue;}")
                    if False:
                        pass
                    else:
                        #widget = QLineEdit(str(df[(database_headers[j]).replace(" ","_")].values[i]).replace(";",", "))
                        widget.setObjectName("database")
                        ##if i % 2 == 0:  # Alternate row colors
                            ##widget.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    widget.setAlignment(QtCore.Qt.AlignCenter)
                    #widget.setStyleSheet("color: black;")
                    try:
                        widget.setReadOnly(True)
                    except:
                        pass #QLabel not have setEditable()
                    widget.clicked.connect(self.viewQuote)
                    self.table_grid.addWidget(widget,i+1,j)

                #make edit and delete toolbutton
                edit = QToolButton()
                edit.setToolTip("Edit")
                edit.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),"images/edit button.png")))
                edit.clicked.connect(lambda: self.editQuote())

                delete = QToolButton()
                delete.setToolTip("Delete")
                delete.setIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),"images/delete button.png")))
                delete.clicked.connect(lambda: self.deleteQuote())

                #alternate colors
                ##if i%2 == 0:
                    ##edit.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    ##delete.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")

                self.table_grid.addWidget(edit,i+1,j+1)
                self.table_grid.addWidget(delete, i+1, j+2)

            for i in large_rows:#rows
                for j in range(len(database_headers)):#columns
                    if type(self.table_grid.itemAtPosition(i + 1, j).widget()) == QLineEdit or type(self.table_grid.itemAtPosition(i + 1, j).widget()) == ClickableLineEdit:
                        widget = self.table_grid.itemAtPosition(i + 1, j).widget()
                        widget.setObjectName("special") #Create special category so not confined by height rules in CSS
                        widget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        except Exception as e:
            sendMessage("Database Table Setup",str(e),self)

    def addTableHeaders(self):
        #self.table_grid = QGridLayout()
        #self.table_grid.setSpacing(0)

        for j in range(len(database_headers)): #TODO: Change part column (or any with multiple lines) with QTextEdit
            wid = ClickableLineEdit(database_headers[j].replace("_"," "))
            wid.setReadOnly(True)
            wid.setAlignment(QtCore.Qt.AlignCenter)
            wid.setObjectName("database-header")
            self.table_grid.addWidget(wid,0,j)

            wid.clicked.connect(self.headerClicked)
            #wid.mousePressEvent(self.organizeQuotes())

    def headerClicked(self):
        try:
            btn = self.sender()
            text = btn.text().replace(" ","_")

            #self.insertDatabaseGrid(self.organizeQuote(self.searched_df,text))
            self.searched_df = self.organizeQuote(self.searched_df,text)
            self.firstSearchInput()
        except Exception as e:
            sendMessage("Database Headers Clicked",str(e),self)

    def organizeQuote(self,df,col):
        try:
            asc = False #Auto sort descending

            if col == self.sorted_by[0]:
                asc = not self.sorted_by[1]
            else:
                self.sorted_by[0] = col
            self.sorted_by[1] = asc

            self.searched_df = df.sort_values(col, ascending=asc)

            return self.searched_df
        except Exception as e:
            sendMessage("Database Organize Quote", str(e), self)

    def editQuote(self):
        try:
            btn = self.sender()
            index = self.table_grid.indexOf(btn)
            row = self.table_grid.getItemPosition(index)[0]

            quote_number = self.table_grid.itemAtPosition(row,0).widget().text()

            #IF same quote already in Active Quote Tab
            if main_window.tabs.widget(1).invoice_number.text() == quote_number:#str(self.searched_df["Quote_Number"].values[row]):
                main_window.tabs.setCurrentIndex(1)  # switch to active quote tab
            elif main_window.tabs.widget(1).invoice_number.text() != "":
                action = self.sendQuoteInUseMsg()

                if action == QMessageBox.Yes:
                    main_window.tabs.widget(1).submitQuote()
                    self.continueEditQuote(quote_number)
                if action == QMessageBox.No:
                    self.continueEditQuote(quote_number)
            else:
                self.continueEditQuote(quote_number)
        except Exception as e:
            sendMessage("Database Edit Quote",str(e),self)

    #Where the quote is put onto the GUI
    def continueEditQuote(self,quote_number,editing=True):
        try:
            #df = self.searched_df
            df = getQuote(quote_number)
            row = 0

            action = ""
            if editing: #if just copying quote, don't check see if being edited by another user
                if df.iloc[row]["isEditing"]:
                    msg = QMessageBox()
                    msg.setWindowTitle("Quote Already Open")
                    msg.setText("Quote is already being edited by another user.\nWould you like to edit anyway?")
                    msg.setIcon(QMessageBox.Critical)
                    msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                    action = msg.exec()

            if action != QMessageBox.No:
                updateIsEditing(str(df.iloc[row]["Quote_Number"]),True)

                #Clears anything in activequote tab
                main_window.tabs.removeTab(1)
                main_window.tabs.insertTab(1,ActiveQuote(),"Active Quote") #TODO: add dialog box if quote being edited
                main_window.tabs.setCurrentIndex(1) #switch to active quote tab

                quote = main_window.tabs.widget(1)

                try:
                    quote.last_time_edited = datetime.strptime(str(df.iloc[row]["Last_Edited"]),'%Y-%m-%d %H:%M:%S.%f')
                except:
                    pass

                #INSERT EVERYTHING

                quantities = str(df["Quantity"].values[row]).split(';')
                part_numbers = str(df["Part_Number"].values[row]).split(';')
                conditions = str(df["Condition"].values[row]).split(';')
                unit_prices = str(df["Unit_Price"].values[row]).split(';')
                line_totals = str(df["Line_Total"].values[row]).split(';')
                stocks = str(df["Stock"].values[row]).split(';')
                notes = str(df["Notes"].values[row]).split(';')

                for i in range(len(part_numbers) - (INITIAL_PART_ROWS-1)): #adds extra parts if needed
                    quote.addTableRow(i+INITIAL_PART_ROWS)

                for i in range(1,quote.table.count()-1): #TODO: make try except for each one? Or since should fill in NONE automatically, should be fine
                    try:
                        quantity = quantities[i-1]
                        if quantity == "None":
                            quantity = '0'
                        quote.table.itemAtPosition(i,2).widget().setText(quantity)
                    except:
                        pass
                    try:
                        quote.table.itemAtPosition(i,3).widget().setText(part_numbers[i - 1])
                    except:
                        pass
                    try:
                        quote.table.itemAtPosition(i,4).widget().setCurrentText(conditions[i - 1])
                    except:
                        pass
                    try:
                        unit_price = unit_prices[i - 1]
                        if unit_price == "None":
                            unit_price = '0'
                        quote.table.itemAtPosition(i,5).widget().setText("${:.2f}".format(float(unit_price)))
                    except:
                        pass
                    try:
                        line_total = line_totals[i - 1]
                        if line_total == "None":
                            line_total = '0'
                        quote.table.itemAtPosition(i,6).widget().setText("${:.2f}".format(float(line_total)))
                    except:
                        pass
                    try:
                        quote.table.itemAtPosition(i,7).widget().setCurrentText(stocks[i - 1])
                    except:
                        pass
                    try:
                        quote.table.itemAtPosition(i,8).widget().setText(notes[i - 1])
                    except:
                        pass

                quote.subject.setText(str(df.iloc[row]["Subject"]))

                quote.invoice_number.setText(str(df["Quote_Number"].values[row]))

                quote.sent_from.setCurrentText(str(df["Sender"].values[row]))

                quote.customer_name.setText(str(df["Customer_Name"].values[row]))

                quote.customer_email.setText(str(df["Customer_Email"].values[row]))

                quote.customer_phone.setText(str(df["Customer_Phone"].values[row]))

                quote.customer_info.setText(str(df["Customer_Notes"].values[row]))

                quote.payment_terms.setCurrentText(str(df["Payment_Terms"].values[row]))

                quote.shipping_method.setCurrentText(str(df["Shipping_Method"].values[row]))

                quote.shipping_charges.setText(str(df["Shipping_Charges"].values[row]))

                #Get additional notes and check appropriate boxes
                additional_notes = str(df["Additional_Notes"].values[row])
                quote.additional_infos.setText(additional_notes)
                for i in range(main_window.tabs.widget(1).note_group_grid.count()):
                    widget = main_window.tabs.widget(1).note_group_grid.itemAt(i).widget()
                    if widget.text() in additional_notes:
                        widget.setChecked(True)

                if df.iloc[row]["Pro_Forma"]:
                    quote.wire_transfer.setChecked(True)

                #Put total into total boxes
                main_window.tabs.widget(1).calculateQuoteTotal()

        except Exception as e:
            sendMessage("Database Edit Quote 2",str(e),self)
            updateIsEditing(str(df.iloc[row]["Quote_Number"]), False)


    def deleteQuote(self):
        try:
            btn = self.sender()
            index = self.table_grid.indexOf(btn)
            row = self.table_grid.getItemPosition(index)[0]
            quote_number = self.table_grid.itemAtPosition(row,0).widget().text()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Delete Quote")
            msg.setText(f"Are you sure you want to delete Quote {quote_number}? This action is not undoable.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            action = msg.exec()

            if action == QMessageBox.Yes:
                deleteQuote(quote_number)

                self.submit_search_keep_place()
        except Exception as e:
            sendMessage("Database Delete Quote", str(e), self)

    def newQuote(self):
        try:
            if main_window.tabs.widget(1).invoice_number.text() != "":
                action = self.sendQuoteInUseMsg()

                if action == QMessageBox.Yes:
                    main_window.tabs.widget(1).submitQuote()
                    self.continueNewQuote()
                if action == QMessageBox.No:
                    self.continueNewQuote()
            else:
                self.continueNewQuote()
        except Exception as e:
            sendMessage("Database New Quote", str(e), self)

    def continueNewQuote(self):
        try:
            #Clears activequote tab and inserts new
            main_window.tabs.removeTab(1)
            main_window.tabs.insertTab(1, ActiveQuote(), "Active Quote")
            main_window.tabs.setCurrentIndex(1)  # switch to active quote tab
            main_window.tabs.setTabEnabled(1,True)

            quote_number = getNewInvoiceNumber()

            #Insert into tab
            main_window.tabs.widget(1).invoice_number.setText(quote_number)
            main_window.tabs.widget(1).subject.setText("RFQ - TRW " + quote_number)

            #Insert into database
            submitNewQuoteToDatabase(quote_number)
        except Exception as e:
            sendMessage("Database New Quote 2", str(e), self)

    def viewQuote(self):
        try:
            btn = self.sender()
            id = btn.text().replace(", ",";")

            index = self.table_grid.indexOf(btn)
            #Column Name for searching in dataframe
            column = self.table_grid.itemAtPosition(0, self.table_grid.getItemPosition(index)[1]).widget().text().replace(" ","_")

            df = self.searched_df.loc[self.searched_df[column] == id]
            html = getHTMLText(str(df["Part_Number"].values[0]).split(';'),str(df["Quantity"].values[0]).split(';'),str(df["Condition"].values[0]).split(';'),
                               str(df["Unit_Price"].values[0]).split(';'),str(df["Line_Total"].values[0]).split(';'),
                               str(df["Stock"].values[0]).split(';'),
                               str(df["Sender"].values[0]),str(df["Sender_Email"].values[0]),
                               str(df["Quote_Number"].values[0]),str(df["Customer_Email"].values[0]),
                               str(df["Subject"].values[0]),str(df["_Date"].values[0]),str(df["Payment_Terms"].values[0]),
                               str(df["Shipping_Method"].values[0]),str(df["Additional_Notes"].values[0]).split("\n"),
                                   df.iloc[0]["Pro_Forma"],df.iloc[0]["Shipping_Charges"],df.iloc[0]["Customer_Notes"])
            ##WAS getViewHTMLText(), but ipmlemented making pdf straight from HTML on page, and since buttons weren't working, switched to getHTMLText()
            main_window.tabs.setCurrentIndex(2)
            main_window.tabs.widget(2).addTabPage(html, str(df["Quote_Number"].values[0]))

        except Exception as e:
            sendMessage("Database View Quote",str(e),self)

    def sendQuoteInUseMsg(self):
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Quote Already Started")
            msg.setText("There is a quote already started. Do you wish to save?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            # msg.buttonClicked.connect(self.continueEdit)

            action = msg.exec()

            return action
        except Exception as e:
            sendMessage("Database Quote In Use Message", str(e), self)

def refresh():
    global main_window
    index = main_window.tabs.currentIndex()
    for ind, tab,text in zip([0,1,2],[Database(),ActiveQuote(),ViewQuotes(),Settings()],["Database","Active Quote","View Quotes","Settings"]):
        main_window.tabs.removeTab(ind)
        main_window.tabs.insertTab(ind,tab,text)
    main_window.tabs.setCurrentIndex(index)
    #TODO: When Refresh, don't delete what in new quote

def setTheme(text):
    try:
        global THEME, Alternating_color, Alternating_font
        THEME = text

        text = text.lower()

        if "classic" in text:
            styleSheet = 'styles/classic/style.qss'
            folder = "classic"
        elif "orange" in text:
            styleSheet = 'styles/dark_orange/style.qss'
            folder = "dark_orange"
        elif "blue" in text:
            styleSheet = 'styles/dark_blue/style.qss'  # Had to change ":/" for files to "./"
            folder = "dark_blue"
        elif "dark" == text:
            styleSheet = 'styles/dark/style.qss'
            folder = "dark"
        elif "light" == text:
            styleSheet = 'styles/light/style.qss'
            folder = "light"
        else:
            styleSheet = 'styles/dark_orange/style.qss'
            folder = "dark_orange"
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)),styleSheet)
        with open(file, "r") as fh:
            app.setStyleSheet(fh.read())
            #app.setStyleSheet(fh.read().replace("./",str(os.path.dirname(os.path.realpath(__file__)))+"/"))

        #apply_stylesheet(app, theme='light_blue.xml') FOR QT-MATERIAL DESIGN - KYLE NOT LIKE

        Alternating_color = ALTERNATING_COLORS[text][0]
        Alternating_font = ALTERNATING_COLORS[text][1]

    except Exception as e:
        print(e)

def storeDatabase(DATABASE_FILE_PATH):
    database_settings = {
        "Database Path": DATABASE_FILE_PATH,
        "Stored Paths": STORED_DATABASE_PATHS
    }

    # Store database file path
    with open(database_settings_file, 'wb') as handle:
        pickle.dump(database_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("Database Settings Stored")

def storeSettings(local = True, shared = True):
    try:
        global shared_settings,local_settings
        if local:
            new_local_settings = {
                "Shared Settings File": str(shared_settings_file),
                "Database Headers": database_headers,
                "Preferred Search": preferred_search,
                "Theme": THEME,
                "Alternating Color": Alternating_color,
                "Alternating Font": Alternating_font,
                "First Time": FIRST_TIME,
                "Quote Directory": SAVE_QUOTES_DIRECTORY,
                "Default User": DEFAULT_USER,
                "Database Searches": DATABASE_SEARCHES,
            }

            with open(local_settings_file, 'wb') as handle:
                pickle.dump(new_local_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)


            print("Local Settings Saved")

        if shared:
            new_shared_settings = {
                "Payment Terms": PAYMENT_TERMS,
                "Shipping Methods": SHIPPING_METHODS,
                "Table Headers": table_headers,
                "Initial Part Rows": INITIAL_PART_ROWS,
                "Sample Notes": sample_notes,
                "Senders": senders,
                "Part Conditions": part_conditions,
                "Stock Options": stock_options,
            }

            with open(shared_settings_file, 'wb') as handle:
                pickle.dump(new_shared_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)

            #with open(shared_settings_file, 'rb') as handle:
                #shared_settings = pickle.load(handle)

            print("Shared Settings Saved")


       # new_settings = {
        #    "Payment Terms": PAYMENT_TERMS,
         #   "Shipping Methods": SHIPPING_METHODS,
          #  "Table Headers": table_headers,
           # "Initial Part Rows": INITIAL_PART_ROWS,
            #"Database Headers": database_headers,
            #"Sample Notes": sample_notes,
            #"Senders": senders,
            #"Preferred Search": preferred_search,
            #"Theme": THEME,
            #"Alternating Color": Alternating_color,
            #"Alternating Font": Alternating_font,
            #"First Time": FIRST_TIME,
            #"Quote Directory": SAVE_QUOTES_DIRECTORY,
            #"Default User": DEFAULT_USER,
            #"Part Conditions": part_conditions,
            #"Stock Options": stock_options,
            #"Database Searches": DATABASE_SEARCHES,
        #}

        # Store data (serialize)
        #with open(settings_file, 'wb') as handle:
         #   pickle.dump(new_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        print("Settings NOT Saved: "+str(e))

def storeDefaultSettings(local = True, shared = True):
    #Store Default Settings

    if local:
        with open(local_settings_file, 'wb') as handle:
            pickle.dump(default_local_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("Default Local Settings Stored")

    if shared:
        ##places default settings in same place as local settings - they should then be copied to where the shared
        ##settings should be
        set = str(local_settings_file)
        set = set[::-1]
        for i in set:
            if i == "/" or i == "\\":
                break
            set = set[1:]
        set = set[::-1]
        shared_settings_location = set + "shared_settings.pickle"
        with open(shared_settings_location, 'wb') as handle:
            pickle.dump(default_shared_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("Default Shared Settings Stored")

def loadSharedVariables(ERRORS_LIST):
    global PAYMENT_TERMS,SHIPPING_METHODS,table_headers,INITIAL_PART_ROWS,sample_notes,senders,stock_options,part_conditions,shared_settings,shared_settings_file
    with open(shared_settings_file, 'rb') as handle:
        shared_settings = pickle.load(handle)
    try:
        PAYMENT_TERMS = shared_settings["Payment Terms"]
        SHIPPING_METHODS = shared_settings["Shipping Methods"]
    except Exception as e:
        PAYMENT_TERMS = default_payment_terms
        SHIPPING_METHODS = default_shipping_methods
        ERRORS_LIST.append(["Cannot load saved payment terms. Default Settings Loaded", e])
    try:
        table_headers = shared_settings["Table Headers"]
    except Exception as e:
        # sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
        table_headers = default_table_headers
        ERRORS_LIST.append(["Cannot load saved table headers. Default Settings Loaded",e])
    try:
        INITIAL_PART_ROWS = shared_settings["Initial Part Rows"]
    except Exception as e:
        # sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
        INITIAL_PART_ROWS = default_initial_part_rows
        ERRORS_LIST.append(["Cannot load initial part rows. Default Settings Loaded",e])
    try:
        sample_notes = shared_settings["Sample Notes"]
    except Exception as e:
        # sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
        sample_notes = default_sample_notes
        ERRORS_LIST.append(["Cannot load saved Customer Notes. Default Settings Loaded",e])
    try:
        senders = shared_settings["Senders"]
    except Exception as e:
        # sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
        senders = default_senders
        ERRORS_LIST.append(["Cannot load saved senders. Default Settings Loaded",e])
    try:
        stock_options = shared_settings["Stock Options"]
    except Exception as e:
        stock_options = default_stock_options
        ERRORS_LIST.append(["Cannot load saved stock options. Default Settings Loaded",e])
    try:
        part_conditions = shared_settings["Part Conditions"]
    except Exception as e:
        part_conditions = default_part_conditions
        ERRORS_LIST.append(["Cannot load saved part conditions. Default Settings Loaded",e])



def getCompleter(type):
    if type == "Part":
        completer_list = getPartNumbers()

    completer = QCompleter(completer_list)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    completer.setCompletionMode(QCompleter.PopupCompletion)

    return completer

def sendMessage(title,message,parent,type = QMessageBox.Warning,btns = QMessageBox.Ok): #TODO: Not working if not in a Widget class
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(type)
    msg.setStandardButtons(btns)
    action = msg.exec_()
    return action

class Error(QMainWindow):
    pass

class Found(Exception):
    pass

def exit_app():
    try:
        updateThread.stop()
        #main_window.tabs.widget(1). TODO if not valid quote, delete
        closeSQLConnection()
    except:
        pass

class FirstDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.UIComponents()
        self.setFixedSize(800,300)

    def UIComponents(self):
        self.setWindowTitle("Initial Setup")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        lbl1 = QLabel("Default User:")
        self.user = QLineEdit()

        lbl2 = QLabel("Directory to store Quote PDFs:")
        self.directory = QLineEdit()

        browse = QPushButton("Browse")
        browse.clicked.connect(self.browseFolders)

        location = os.path.join(os.path.expanduser('~'), 'Documents', 'Quotes')
        self.directory.setText(str(location))

        lay1 = QVBoxLayout()
        lay1.addWidget(lbl1)
        lay1.addWidget(self.user)
        lay1.setAlignment(QtCore.Qt.AlignCenter)

        lay3 = QHBoxLayout()
        lay3.addWidget(self.directory)
        lay3.addWidget(browse)

        lay2 = QVBoxLayout()
        lay2.addWidget(lbl2)
        lay2.addLayout(lay3)
        lay2.setAlignment(QtCore.Qt.AlignCenter)

        lbl4 = QLabel("Select Database")
        browse_data = QPushButton("Browse")
        browse_data.clicked.connect(self.browseDatabase)
        self.database = QLineEdit()
        self.database.setText(str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/TRW Quote Database.accdb")))
        lay5 = QHBoxLayout()
        lay5.addWidget(self.database)
        lay5.addWidget(browse_data)

        lay4 = QVBoxLayout()
        lay4.addWidget(lbl4)
        lay4.addLayout(lay5)
        lay4.setAlignment(QtCore.Qt.AlignCenter)

        #Shared Settings File
        s_lbl = QLabel("Select Shared Settings File")
        browse_settings = QPushButton("Browse")
        browse_settings.clicked.connect(self.browseSettings)
        self.settings = QLineEdit()
        self.settings.setText("//trw_nas/TRW Shared Folder/NEW Quote Database/shared_settings.pickle")

        slay = QHBoxLayout()
        slay.addWidget(self.settings)
        slay.addWidget(browse_settings)

        sslay = QVBoxLayout()
        sslay.addWidget(s_lbl)
        sslay.addLayout(slay)
        sslay.setAlignment(QtCore.Qt.AlignCenter)



        okay = QPushButton("Okay")
        okay.clicked.connect(self.tryClose)
        lay3 = QHBoxLayout()
        lay3.addWidget(okay)

        main_lay = QVBoxLayout()
        main_lay.addLayout(lay1)
        main_lay.addLayout(lay2)
        main_lay.addLayout(lay4)
        main_lay.addLayout(sslay)
        main_lay.addLayout(lay3)

        self.setLayout(main_lay)

    def tryClose(self):
        if not os.path.exists(self.database.text()):
            msg = QMessageBox()
            msg.setText("Database Does not Exist")
            msg.setWindowTitle("Database Error")
            msg.exec()
        elif not os.path.exists(self.settings.text()):
            msg = QMessageBox()
            msg.setText("Database Does not Exist")
            msg.setWindowTitle("Database Error")
            msg.exec()
        else:
            self.close()

    def browseFolders(self):
        destDir = QFileDialog.getExistingDirectory(None,'Open working directory',
                        os.path.join(os.path.expanduser("~"),"Documents"),QFileDialog.ShowDirsOnly)
        self.directory.setText(str(destDir))

    def browseDatabase(self):
        database_path = QFileDialog.getOpenFileName(self,"Open database",
                                                    os.path.join(os.path.expanduser("~"),"Documents"),'Microsoft Access (*.accdb)')
        self.database.setText(str(database_path[0]))

    def browseSettings(self):
        settings_path = QFileDialog.getOpenFileName(self,"Open database",
                                                    os.path.join(os.path.expanduser("~"),"Documents"),'PICKLE File (*.pickle)')
        self.settings.setText(str(settings_path[0]))

##Thread: updates application every 600 seconds
pause_time = 600
class updateApp(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        #Initially wait 5 seconds to check
        time.sleep(5)
        try:
            global main_window,shared_settings_file,shared_settings

            while not self._stop_event.is_set():
                # Check for shared settings update

                # Load Shared Settings
                try:
                    with open(shared_settings_file, 'rb') as handle:
                        new_shared_settings = pickle.load(handle)
                except Exception as e:
                    print(e)

                #Compare new and old shared settings
                if not new_shared_settings == shared_settings:
                    print("Get New Settings")

                    shared_settings = new_shared_settings
                    loadSharedVariables()

                    #update GUI if user not on that page
                    #if not main_window.tabs.widget(3).tool_box.currentIndex() == 3:
                    #Update settings tab
                    main_window.tabs.widget(3).updateUserStockCondWid()


                count = 0
                while not self._stop_event.is_set() and count < pause_time:
                    #check every second but only check main loop every pause_time seconds
                    time.sleep(1)
                    count += 1
        except Exception as e:
            print(e)

if __name__ == '__main__':
    #storeDefaultSettings() ##UNCHECK FOR MAKING NEW PICKLE FILES - also do one at end of file

    #Make list for any errors done before GUI setup, so later can send message to user
    ERRORS_LIST = []
    log.basicConfig(filename="app.log",filemode='a',level=log.DEBUG)

    try:
        # Load local settings
        try:
            with open(local_settings_file, 'rb') as handle:
                local_settings = pickle.load(handle)

        except Exception as e:
            # sendMessage("Error", "Error loading settings", parent=error, type = QMessageBox.Critical)
            ERRORS_LIST.append(["Error loading settings",e])

        try:
            database_headers = local_settings["Database Headers"]
        except Exception as e:
            #sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            database_headers = default_database_headers
            ERRORS_LIST.append(["Cannot load Saved Database Headers. Default Settings Loaded",e])
        try:
            preferred_search = local_settings["Preferred Search"]
        except Exception as e:
            #sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            preferred_search = default_preferred_search
            ERRORS_LIST.append(["Cannot load Preferred Search. Default Settings Loaded",e])
        try:
            THEME = local_settings["Theme"]
            Alternating_color = local_settings["Alternating Color"]
            Alternating_font = local_settings["Alternating Font"]
        except Exception as e:
            #sendMessage("Error", "Cannot load saved theme. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            THEME = default_theme
            Alternating_color = default_alternating_color
            Alternating_font = default_alternating_font
            ERRORS_LIST.append(["Cannot load Saved Theme. Default Settings Loaded",e])
        try:
            FIRST_TIME = local_settings["First Time"]
        except Exception as e:
            FIRST_TIME = True
        try:
            SAVE_QUOTES_DIRECTORY = local_settings["Quote Directory"]
        except Exception as e:
            #SAVE_QUOTES_DIRECTORY =
            pass
        try:
            DEFAULT_USER = local_settings["Default User"]
        except Exception as e:
            ERRORS_LIST.append(["Cannot load Default User. Default Settings Loaded",e])
        try:
            DATABASE_SEARCHES = local_settings["Database Searches"]
        except Exception as e:
            ERRORS_LIST.append(["Cannot load Database Searches. Default Settings Loaded",e])
            DATABASE_SEARCHES = default_database_searches
            log.exception(e)

        # app = QApplication([])
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(exit_app)
        setTheme(THEME)
        #apply_stylesheet(app, theme='light_cyan_500.xml')
        app.setStyle('Fusion')

        # If first time running app, setup initial features
        #FIRST_TIME = True #TODO: Take out once actually need to work
        if FIRST_TIME:
            window = FirstDialog()
            window.exec()

            DEFAULT_USER = window.user.text()  # TODO: If default user not in, ask for email and make new one
            # TODO: Or just on first time, make them put in automatically
            SAVE_QUOTES_DIRECTORY = f"""{window.directory.text()}"""
            DATABASE_FILE_PATH = f"""{window.database.text()}"""
            shared_settings_file = f"""{window.settings.text()}"""
            STORED_DATABASE_PATHS = [DATABASE_FILE_PATH]
            FIRST_TIME = False

            # Check save_quotes_directory to see if actual path - if not, create it
            if not os.path.exists(SAVE_QUOTES_DIRECTORY):
                os.makedirs(SAVE_QUOTES_DIRECTORY)
                print("New Directory made: " + SAVE_QUOTES_DIRECTORY)

            storeSettings(shared = False)

            storeDatabase(DATABASE_FILE_PATH)
        else:
            #Get shared_file_path
            try:
                shared_settings_file = local_settings["Shared Settings File"]
            except Exception as e:
                log.exception(e)

        #Load Shared Settings
        try:
            with open(shared_settings_file, 'rb') as handle:
                shared_settings = pickle.load(handle)

        except Exception as e:
            #sendMessage("Error", "Error loading settings", parent=error, type = QMessageBox.Critical)
            log.exception(e)

        # Load settings into respective variables
        loadSharedVariables(ERRORS_LIST)


        #Establish connection to database
        try:
            with open(database_settings_file, 'rb') as handle:
                database_settings = pickle.load(handle)

            database_file = database_settings["Database Path"]
        except Exception as e:
            ERRORS_LIST.append(["Cannot load database settings.",e])
        try:
            STORED_DATABASE_PATHS = database_settings["Stored Paths"]
        except Exception as e:
            ERRORS_LIST.append(["Cannot load Database Paths",e])
            STORED_DATABASE_PATHS = []
            #STORED_DATABASE_PATHS.append()
        try:
            connectDatabase(database_file)
        except Exception as e:
            ERRORS_LIST.append(["COULD NOT CONNECT TO DATABASE",e])

        #gets list of headers in database
        try:
            df = getQuote("")
            DATABASE_HEADERS = list(df.columns)
        except:
            DATABASE_HEADERS = default_database_headers

        #Actual main interface
        main_window = MainWindow()

        updateThread = updateApp()
        updateThread.start()

        #Send Errors to user
        for li in ERRORS_LIST:
            sendMessage(li[0],str(li[1]),main_window)

        #storeDefaultSettings()

        sys.exit(app.exec_())

    except Exception as e:
        print(e)



