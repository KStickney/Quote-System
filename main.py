#Settings: Allow how many columns, what size each column, if combobox or pure plugin, if and where completer draw from
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import math
import pandas as pd
import pickle


from CustomClasses import *
from database import *
from pdf.pdfcreator import *

SAVE_QUOTES_LOCATION = "C:/Users/Patrick/Desktop/"


#Default Settings
default_payment_terms = {"Credit Card":"CC","NET 30":"NET 30","NET 60":"NET 60","Wire Transfer":"TT"}
default_shipping_methods = ["UPS Ground","UPS NDA","UPS 2nd NDA","FedEx Ground","FedEx NDA","DLH"]
default_table_headers = ["Item","Quantity", "Part Number","Condition","Unit Price","Line Total","Stock","Notes"]
default_initial_part_rows = 3 #How many rows show initially in quote
default_database_headers = ["Quote Number","Customer Email","Part Number",]
default_sample_notes = ["New Warranty -- 1 year", "Refurbished Warranty -- 1 year","*****************************"]
default_senders = {"Kyle Stickney":"kyle@trwelectric.com",
                   "Tim Stickney": "tim@trwelectric.com",
                   "Nathan": "nathan@trwelectric.com"
                   }
default_preferred_search = "Part"
default_theme = "Dark, Orange"
default_alternating_color = "rgb(231,231,227)" #TODO: Link csv file to these so when change all alternate ones change
default_alternating_font = "black" #TODO: when delete a row, change alternate rows

#Regular variables
completer_list = ["Germany", "Spain", "France", "Norway","Norwegian"] #TODO: Make completer both inline and popup
completer = QCompleter(completer_list)
completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
completer.setCompletionMode(QCompleter.PopupCompletion)

DATABASE_HEADERS = []
DATABASE_FILE = "./TRW Quote Database.csv"
ALTERNATING_COLORS = {
                "dark, orange": ("rgb(231,231,227)","black"),
                "dark, blue": ("rgb(231,231,227)","black"),
                "classic": ("rgb(228,246,248)","black"),
                "dark": ("rgb(231,231,227)","black"),
                "light": ("rgb(231,231,227)","black"),
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
}
settings_file = "./data/settings.pickle" #For pickle, could put all variables inside dictionary or list or use editorconfig file


class MainWindow(QMainWindow): #TODO: make function for when click into and out of each tab + warning message box for Quote tab
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TRW Quote System")
        logo = QIcon('./images/TRW Supply Logo.jpg')
        self.setWindowIcon(logo)

        self.styleSheet = "./stylesheets/Main Stylesheet.css"
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.UIComponents()
        self.showMaximized()

    def UIComponents(self):

        self.tabs = TabWidget()#QTabWidget()
        self.tabs.addTab(Database(), "Database")
        self.tabs.addTab(ActiveQuote(),"Active Quote")
        self.tabs.addTab(ViewQuotes(), "View Quotes")
        self.tabs.addTab(Settings(),"Settings")

        self.tabs.tabBarClicked.connect(self.handleTabbarClicked)

        self.setCentralWidget(self.tabs)

    def handleTabbarClicked(self,index):
        #self.tabs.tabText(index)
        try:
            if index == 1: #Active Quote
                if self.tabs.widget(index).invoice_number.text() == "":
                    number = getNewInvoiceNumber()
                    self.tabs.widget(index).invoice_number.setText(number)

            if index == 0: #Databse
                pass #TODO: do nothing, or resubmit search (if not clear search bar)

            if index == 2: #View Quotes
                if not self.tabs.widget(index).dock_widget.isVisible():
                    self.tabs.widget(index).dock_widget.setVisible(True)
                    self.tabs.widget(index).dock_widget.setFloating(False)
                if self.tabs.widget(index).dock_widget.isFloating():
                    self.tabs.widget(index).dock_widget.setFloating(False)
        except Exception as e:
            print(e)

class ActiveQuote(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = "./stylesheets/Quote Stylesheet.css"
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.table_row_count = 0

        self.UIComponents()

    def UIComponents(self):
        #Invoice Header
        self.invoice_number = QLineEdit()
        self.invoice_number.setPlaceholderText("Invoice Number")
        self.invoice_number.setObjectName("invoice")

        self.sent_from_label = QLabel("Sent From:")
        self.sent_from_label.setObjectName("invoice")
        self.sent_from_label.setAlignment(QtCore.Qt.AlignVCenter)

        self.sent_from = QComboBox()
        self.sent_from.addItems(senders.keys())

        lay = QHBoxLayout()
        lay.setSpacing(0)
        lay.addWidget(self.sent_from_label)
        lay.addWidget(self.sent_from)

        self.invoice_layout = QHBoxLayout()
        self.invoice_layout.addWidget(self.invoice_number)
        self.invoice_layout.addLayout(lay)
        #self.invoice_layout.addWidget(self.sent_from_label)
        #self.invoice_layout.addWidget(self.sent_from)


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
        #self.customer_layout.addWidget(self.customer_name)
        self.customer_layout.addLayout(layout)
        self.customer_layout.addWidget(self.customer_info)


        #SHIPPING
        p = QLabel("Payment Terms:")
        s = QLabel("Shipping Method:")
        sc = QLabel("Shipping Charges:")
        for label in (p,s,sc):
            label.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignRight)
            label.setObjectName("shipping")

        self.payment_terms = QComboBox()
        self.payment_terms.setEditable(False)
        self.payment_terms.addItems(PAYMENT_TERMS.keys())

        self.shipping_method = QComboBox()
        self.shipping_method.setEditable(False)
        self.shipping_method.addItems(SHIPPING_METHODS)

        self.shipping_charges = QLineEdit()

        for item in (self.payment_terms,self.shipping_method,self.shipping_charges):
            item.setObjectName("shipping")

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


        #Where table grid used to be
        #ITEM TABLE
        self.add_table_item_btn = QPushButton("Add Item")
        self.add_table_item_btn.setObjectName("add-item")
        #self.add_table_item_btn.clicked.connect(lambda: self.add_table_item(None,True))
        self.add_table_item_btn.clicked.connect(lambda: self.addTableRow(i=None, remove_btn=True))

        self.del_table_item_btn = QPushButton("Delete Item")
        self.del_table_item_btn.setObjectName("add-item")
        #self.del_table_item_btn.clicked.connect(lambda: self.deleteTableItem())
        self.del_table_item_btn.clicked.connect(lambda: self.deleteTableRow())

        self.add_note_btn = QCheckBox("Add Note")
        self.add_note_btn.setObjectName("add-item")
        #self.add_note_btn.toggled.connect(lambda: self.addNoteCol())
        self.add_note_btn.toggled.connect(lambda: self.toggleNoteCol())
        self.add_note_btn.setChecked(False)

        #PART NUMBER TABLE
        #self.table = QGridLayout()
        #self.table.setSpacing(0)
        #self.table.setAlignment(QtCore.Qt.AlignCenter)
        #for i in range(INITIAL_PART_ROWS):
            #self.add_table_item(i)
       # self.addNoteCol()

        self.table = CustomGridLayout()
        self.table.setSpacing(0)
        #self.table.setAlignment(QtCore.Qt.AlignCenter)
        for i in range(INITIAL_PART_ROWS):
            self.addTableRow(i)
        self.toggleNoteCol()

        self.table_buttons = [self.add_table_item_btn,self.del_table_item_btn,self.add_note_btn]
        i = INITIAL_PART_ROWS + 1
        self.addTableButtons2(i)


        self.note_group = QGroupBox("Notes") #Group Box for the quote notes
        self.note_group.setCheckable(False)
        self.note_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed) #.Preferred
        self.note_group_grid = QGridLayout()
        self.note_group.setLayout(self.note_group_grid)
        NOTE_COLS = 2
        NOTE_ROWS = math.ceil(len(sample_notes) / NOTE_COLS) #Rounds up so another col is not created
        i = 0
        j=0
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
        self.save_btn.clicked.connect(lambda: self.submitQuote())

        self.save_and_exit_btn = QPushButton("Save and Close")
        self.save_and_exit_btn.clicked.connect(lambda: self.saveAndClose())

        self.close_btn = QPushButton("Close")

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
        self.main_layout.addLayout(self.table) #TODO: Fix spacing, table taking up extra space
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

    def add_table_item(self,i,remove_btn = False): #TODO: Make certain ones QComboBoxes - allow in settings
        try:
            if remove_btn:
                for btn in self.table_buttons:
                    self.table.removeWidget(btn)
                i = self.table_row_count-1
                self.table_row_count -= 1

            if i != 0:
                self.table.addWidget(QCheckBox(), i, 0)
            for j in range(len(table_headers)):
                cell = QLineEdit()
                cell.setAlignment(QtCore.Qt.AlignCenter)

                if i == 0: #Means Header
                    cell.setReadOnly(True)
                    cell.setObjectName("table-header")
                    cell.setText(table_headers[j])
                else:
                    if i % 2 == 1:
                        cell.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")

                    if table_headers[j] == "Part Number": # TODO: Change to whatever field in settings
                        cell.setValidator(CapsValidator())
                        cell.setCompleter(getCompleter("Part"))
                    cell.setObjectName("table")

                if j == 0:
                    cell.setFixedWidth(100)
                if j == (len(table_headers)-1) and not self.add_note_btn.isChecked(): #Notes Column
                    cell.hide()
                self.table.addWidget(cell, i, j+1)
            self.table_row_count += 1

            if remove_btn:
                i = self.table_row_count + 1
                self.addTableButtons(i)
        except Exception as e:
            print(e)

    def addTableRow(self,i,remove_btn = False): #TODO: Fix messing up when lots of rows; maybe not use table.count() directly?
        try:
            if remove_btn:
                #for btn in self.table_buttons:
                    #self.table.removeWidget(btn)
                #i = self.table_row_count - 1
                #self.table_row_count -= 1

                #i = self.table.count()-1
                i = self.table_row_count-1
                self.table.deleteRow(i+1)
                self.table_row_count -= 1

            wid = QCheckBox()
            if i == 0:
                sp_retain = wid.sizePolicy()
                sp_retain.setRetainSizeWhenHidden(True)
                wid.setSizePolicy(sp_retain)
                wid.hide()
            self.table.addWidget(wid, i, 0)

            for j in range(len(table_headers)):
                cell = QLineEdit()
                cell.setAlignment(QtCore.Qt.AlignCenter)

                if i == 0:  # Means Header
                    cell.setReadOnly(True)
                    cell.setObjectName("table-header")
                    cell.setText(table_headers[j])

                    if j == 0: #means "ITEM" Header
                        cell.setFixedWidth(80)
                    if j == 1: #QUANTITY
                        cell.setFixedWidth(100)
                else:

                    if table_headers[j] == "Part Number":
                        cell.setValidator(CapsValidator())
                        cell.setCompleter(getCompleter("Part"))

                    if j == 0: #ITEM number
                        cell.setFixedWidth(80)
                        cell.setReadOnly(True)
                        cell.setText(str(i))
                    if j == 1: #Quantity only accept integers
                        cell.setValidator(QIntValidator())
                        cell.setFixedWidth(100)
                    if table_headers[j] == "Condition": #CONDITIONS #todo: make width same: maybe switch back to gridlayout??
                        cell = QComboBox()
                        cell.setEditable(True)
                        default_conditions = ["New","Used","Refurbished"]
                        cell.addItems(default_conditions)
                    if j == 4 or j == 5: # make unit price, line total only accept floats
                        cell.setValidator(QDoubleValidator())
                    if j == 1 or j == 4: #make quantity and unity price change line total
                        cell.textChanged.connect(lambda: self.calculateLineTotal())
                    if table_headers[j] == "Stock": #STOCK
                        cell = QComboBox()
                        cell.setEditable(True)
                        default_stock = ["New In Stock","1-3 Week Lead Time"]
                        cell.addItems(default_stock)
                    if j == (len(table_headers) - 1) and not self.add_note_btn.isChecked():  # Hide Notes Column
                        cell.hide()

                    if i % 2 == 1:
                        cell.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    cell.setObjectName("table")

                self.table.addWidget(cell,i,j+1)

            self.table_row_count += 1

            if remove_btn:
                i = self.table_row_count + 1
                self.addTableButtons2(i)

        except Exception as e:
            print(e)

    def calculateLineTotal(self):
        try:
            btn = self.sender()

            #iterate through each cell one to find what row it is in
            try:
                for row in range(1,self.table.count()-1):
                    for col in range(self.table.itemAt(row).layout().count()):
                        if self.table.itemAt(row).layout().itemAt(col).widget() == btn:
                            index = row
                            raise Found
            except Found:
                pass

            #get quantity
            quantity = self.table.itemAt(index).layout().itemAt(2).widget().text()
            if quantity == "":
                quantity = 0
            else:
                quantity = int(quantity)

            #get unit price
            unit = self.table.itemAt(index).layout().itemAt(5).widget().text()
            if unit == "":
                unit = 0
            else:
                unit = float(unit)
                # put unit price back in formatted to two decimal places
                #self.table.itemAt(index).layout().itemAt(5).widget().setText(str(format(unit, '.2f')))
                #taken out - won't let keep typing

            #insert line total formated to two decimal places
            self.table.itemAt(index).layout().itemAt(6).widget().setText(str(format(quantity *unit, '.2f')))

        except Exception as e:
            print(e)


    def addTableButtons(self,i):
        for j in range(len(self.table_buttons)):
            v = QHBoxLayout()
            v.addWidget(self.table_buttons[j])
            v.setStretch(1,0)
            #self.table.addWidget(self.table_buttons[j],i,j+1)
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

    def deleteTableItem(self): #TODO: Fix mashup delete
        #TOOD: When delete, go through and redo alternating cell and item number
        try:
            rows = self.checkTableCheckboxes()
            for i in rows:
                for j in range(self.table.columnCount()):
                    self.table.removeWidget(self.table.itemAtPosition(i,j).widget())
                self.table_row_count -= 1
        except Exception as e:
            print(e)

    def deleteTableRow(self):
        try:
            rows = self.checkTableCheckboxes2()
            for i in rows:
                self.table.deleteRow(i)
        except Exception as e:
            print(e)

    def toggleNoteCol(self):
        try:
            j = self.table.columnCount() - 1

            if self.add_note_btn.isChecked():
                self.table.showCol(j)
            else:
                self.table.hideCol(j)
        except Exception as e:
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
            main_window.tabs.removeTab(1)
            main_window.tabs.insertTab(1,ActiveQuote(),"Active Quote")
            main_window.tabs.setCurrentIndex(0)
        except Exception as e:
            print(e)

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
                                   str(df["Shipping_Method"].values[0]), str(df["Additional_Notes"].values[0]).split("\n"))

            makeQuotePDF(html,SAVE_QUOTES_LOCATION+"INVOICE")
        except Exception as e:
            print(e)

    def submitQuote(self):
        try: #to convert "None" to Proper None:    x = None if x == 'None' else x

            #for row in range(1, self.table.count() - 1): #Checks to see if missing info #TODO: Want??
                #for col in range(2, self.table.itemAt(row).count()):
                    #if self.table.itemAt(row).layout().itemAt(col).widget().text() == "":
                        #sendMessage("Missing Info",
                                    #"There are columns with missing information. Would you like to continue?",parent = main_window)

            quote_number = self.invoice_number.text()

            quantities = ""
            part_numbers = ""
            conditions = ""
            unit_prices = ""
            line_totals = ""
            stocks = ""
            notes = ""

            for row in range(1,self.table.count()-1):
                try:
                    if self.table.itemAt(row).layout().itemAt(3).widget().text() != "": #if there is a part number, then save row
                        if self.table.itemAt(row).layout().itemAt(2).widget().text() != "":
                            quantities += self.table.itemAt(row).layout().itemAt(2).widget().text() + ";"
                        else:
                            quantities += "None;"

                        part_numbers += self.table.itemAt(row).layout().itemAt(3).widget().text() + ";"

                        if self.table.itemAt(row).layout().itemAt(4).widget().text() != "":
                            conditions += self.table.itemAt(row).layout().itemAt(4).widget().text() + ";"
                        else:
                            conditions += "None;"
                        if self.table.itemAt(row).layout().itemAt(5).widget().text() != "":
                            unit_prices += self.table.itemAt(row).layout().itemAt(5).widget().text() + ";"
                        else:
                            unit_prices += "None;"
                        if self.table.itemAt(row).layout().itemAt(6).widget().text() != "":
                            line_totals += self.table.itemAt(row).layout().itemAt(6).widget().text() + ";"
                        else:
                            line_totals += "None;"
                        if self.table.itemAt(row).layout().itemAt(7).widget().text() != "":
                            stocks += self.table.itemAt(row).layout().itemAt(7).widget().text() + ";"
                        else:
                            stocks += "None;"
                        if self.table.itemAt(row).layout().itemAt(8).widget().text() != "":
                            notes += self.table.itemAt(row).layout().itemAt(8).widget().text() + ";"
                        else:
                            notes += "None;"
                except:
                    pass

            #delete semicolon at end
            quantities = quantities[:-1]
            part_numbers = part_numbers[:-1]
            conditions = conditions[:-1]
            unit_prices = unit_prices[:-1]
            line_totals = line_totals[:-1]
            stocks = stocks[:-1]
            notes = notes[:-1]

            sender = self.sent_from.currentText()

            sender_email = senders[sender]

            customer_name = self.customer_name.text()

            customer_email = self.customer_email.text()

            customer_phone = self.customer_phone.text()

            customer_notes = self.customer_info.toPlainText() #TODO: Fix inputing new line

            additional_notes = self.additional_infos.toPlainText()

            payment_terms = self.payment_terms.currentText()

            shipping_method = self.shipping_method.currentText()

            shipping_charges = self.shipping_charges.text()

            submitQuoteToDatabase(quote_number=quote_number,quantities=quantities,part_numbers=part_numbers,
                                  conditions=conditions,unit_prices=unit_prices,line_totals=line_totals,stock=stocks,
                                  notes=notes,sender=sender,sender_email=sender_email,customer_name=customer_name,customer_email=customer_email,
                                  customer_phone=customer_phone,customer_notes=customer_notes,additional_notes=additional_notes,
                                  payment_terms=payment_terms,shipping_method=shipping_method,shipping_charges=shipping_charges)

        except Exception as e:
            print(e)



class ViewQuotes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UIComponents()
        self.showMaximized()

    def UIComponents(self):
        size = self.size()
        print(size)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.tabs.removeTab(index))
        self.tabs.setStyleSheet("QTabBar::tab{max-height:10px;}")

        self.dock_widget = QDockWidget("Active Quotes")
        self.dock_widget.setWidget(self.tabs)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.dock_widget)

        self.dock_widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.setDockOptions(self.GroupedDragging | self.AllowTabbedDocks | self.AllowNestedDocks)
        self.setTabPosition(QtCore.Qt.AllDockWidgetAreas, QTabWidget.North)
        self.tabifyDockWidget(self.dock_widget,self.dock_widget)

    def addTabPage(self,html,quote_number):
        view = QWebEngineView()
        view.setHtml(html)
        self.tabs.addTab(view,quote_number)

        index = self.tabs.indexOf(view)
        self.tabs.setCurrentIndex(index)


class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = "./stylesheets/Settings Stylesheet.css"
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.UIComponents()

    def UIComponents(self):
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

        #DATABASE HEADERS
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
        for btn in (self.database_submit_btn,self.database_add_col_btn, self.database_del_col_btn):
            self.database_btn_layout.addWidget(btn)
            btn.setObjectName("database-edit")

        self.database_layout = QVBoxLayout()
        self.database_layout.addLayout(self.database_edit_layout)
        self.database_layout.addLayout(self.database_btn_layout)
        self.database_widget = QWidget()
        self.database_widget.setLayout(self.database_layout)

        #Setup Toolbox and main layout for tab
        self.tool_box.addItem(self.style_group,"Style")
        self.tool_box.addItem(self.refresh_table_maker(),"Item Table")
        self.tool_box.addItem(self.database_widget,"Database Headers")
        self.tool_box.addItem(QWidget(),"")
        self.tool_box.setContentsMargins(80,80,100,100)

        self.tool_box.setCurrentIndex(self.tool_box.count()-1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tool_box)
        self.setLayout(self.main_layout)

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
            self.table_layout.addLayout(self.table_submit_layer) #TODO: Add Database header tab
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
            global Alternating_color,Alternating_font, ALTERNATING_COLORS #TODO: Fix already alternated rows if switch colors

            btn = self.sender()
            text = btn.text()

            setTheme(text)

            storeSettings()
            #refresh()

        except Exception as e:
            print(e,535)

    def submitHeaders(self): #TODO: Update database tab - keep search if search is up?
        #TODO: Possibly select which one want to delete? how select two objects at once
        try:
            global database_headers

            for i in range(len(database_headers)):
                database_headers.pop()

            for i in range(self.database_edit_layout.count()):
                database_headers.append(self.database_edit_layout.itemAt(i).widget().currentText())
            storeSettings()
        except Exception as e:
            print(e)

    def addCol(self,header):
        wid = QComboBox()
        wid.addItems(DATABASE_HEADERS)  # TODO: CHANGE TO FULL LIST OF HEADERS IN DATABASE
        wid.setCurrentText(header.replace(" ","_"))
        wid.setObjectName("database-header")
        self.database_edit_layout.addWidget(wid)

    def delCol(self):
        length = self.database_edit_layout.count()-1
        if length > 0:
            wid = self.database_edit_layout.itemAt(length).widget()
            self.database_edit_layout.removeWidget(wid)

class Database(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = "./stylesheets/Database Stylesheet.css"
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.sorted_by = ["",""]

        self.UIComponents()

    def UIComponents(self):
        self.new_quote_btn = QPushButton("New Quote")
        self.new_quote_btn.clicked.connect(lambda: self.newQuote())

        self.refresh_btn = QPushButton("Refresh")

        self.search_by_box2 = QComboBox()
        self.addComboOptions(self.search_by_box2)

        self.search_box2 = QLineEdit()  # TODO: Make different completer based on whay search by is
        self.search_box2.returnPressed.connect(self.onSubmitSearch)
        self.search_box2.setPlaceholderText("Search")
        self.search_box2.setAlignment(QtCore.Qt.AlignCenter)

        self.search_by_box = QComboBox()
        self.addComboOptions(self.search_by_box)

        #self.search_by_box.setCurrentText("Search by part number")
        #search_list = ["Search by part","Search by quote","Search by name"]
        #self.search_by_box.addItems(search_list)

        self.search_box = QLineEdit() #TODO: Make different completer based on whay search by is
        self.search_box.returnPressed.connect(self.onSubmitSearch)
        self.search_box.setPlaceholderText("Search")
        self.search_box.setAlignment(QtCore.Qt.AlignCenter)

        self.search_btn = QPushButton(QIcon("./images/search image.png"),"Search")
        self.search_btn.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.search_btn.clicked.connect(self.onSubmitSearch)

        self.search_layer = QHBoxLayout()
        for wid in (self.new_quote_btn, self.refresh_btn,self.search_by_box2,self.search_box2,
                self.search_by_box,self.search_box,self.search_btn):
            self.search_layer.addWidget(wid)
            wid.setObjectName("search")
        self.search_layer.setAlignment(QtCore.Qt.AlignRight)

        self.table_grid = QGridLayout()
        self.table_grid.setSpacing(0)
        self.table_grid.setVerticalSpacing(0)
        self.table_grid.setSizeConstraint(QLayout.SetMinimumSize)
        self.addTableHeaders()

        #OPENS DATABASE and reads as a pandas dataframe and inserts into grid
        #df = pd.read_csv(DATABASE_FILE) #TODO: change to getQuotes() and select how many want to show initially
        #self.insertDatabaseGrid(df, df)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.search_layer)
        self.main_layout.addLayout(self.table_grid)
        #self.main_layout.addWidget(self.scroll_area)
        #self.setLayout(self.main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        wid = QWidget()
        wid.setLayout(self.main_layout)
        self.scroll_area.setWidget(wid)
        lay = QVBoxLayout()
        lay.addWidget(self.scroll_area)
        self.setLayout(lay)

    def addComboOptions(self, box):
        self.search_dictionary = {}
        #for search in database_headers: #only specific few
        for search in DATABASE_HEADERS: #So can choose from all database headers
            self.search_dictionary["Search by " + search.replace("_"," ")] = search.replace(" ","_") #used to be search.lower for the key
            # self.search_by_box.addItem("Search by "+search.lower())
        box.addItems(self.search_dictionary.keys())

        for i in range(box.count()):
            if preferred_search.lower() in box.itemText(i).lower():
                box.setCurrentText(box.itemText(i))

    def onSubmitSearch(self): #TODO: make so can search IN and not just ==
        try:

            #Get search texts
            search_by1 = self.search_dictionary[self.search_by_box.currentText()]
            search1 = self.search_box.text()

            search_by2 = self.search_dictionary[self.search_by_box2.currentText()]
            search2 = self.search_box2.text()

            #captialize if part number
            if search_by1 == "Part_Number":
                search1 = search1.upper()
            if search_by2 == "Part_Number":
                search2 = search1.upper()

            ##df = getQuotes() #gets all quotes

            if search1 == "" and search2 == "":
                searched_df = getQuotes()

            #SEARCHING USING ONE
            elif search1 == "" or search2 == "":
                if search1 == "":
                    search = search2
                    search_by = search_by2
                else:
                    search = search1
                    search_by = search_by1

                #searched_df = df[df[search_by] == search]
                ##searched_df = df[search in df[search_by]]
                #self.searched_df = df.loc[:,search in df[search_by]]
                searched_df = getQuotes1(search,search_by)

            # SEARCH USING TWO
            else:
                ##searched_df = df[(df[search_by1] == search1) & (df[search_by2] == search2)]
                #self.searched_df = df.loc[:,(df[search_by1] == search1) & (df[search_by2] == search2)]
                searched_df = getQuotes2(search1,search2,search_by1,search_by2)

            #Organize initially by descending Quote Number
            self.searched_df = searched_df.sort_values("Quote_Number",ascending=False)
            self.sorted_by[0] = "Quote_Number"
            self.sorted_by[1] = False

            # ADD ROWS INTO TABLE
            self.insertDatabaseGrid(self.searched_df)
        except Exception as e:
            print(e)

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

            for i in range(len(df)): #Rows in df #TODO: What if multiple part numbers? How display, how put into csv, how search
                for j in range(len(database_headers)): #Col in grid
                    widget = ClickableLineEdit(str(df[(database_headers[j]).replace(" ", "_")].values[i]).replace(";", ", "))
                    maxwidth = QFontMetrics(widget.font()).maxWidth()
                    textlen = len(widget.text())
                    if textlen > (widget.width()/maxwidth):
                        widget = QLabel(str(df[(database_headers[j]).replace(" ", "_")].values[i]).replace(";", ", ")) #TODO: Change entire row to that height
                        #TODO: Add QLabel CSS to every style to be just like QLineEdits
                        widget.setWordWrap(True)
                        if i not in large_rows:
                            large_rows.append(i)
                        #widget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding)
                    if j == 0: #allows quote number to be clicked to view quote
                        #widget = ClickableLineEdit(str(df[(database_headers[j]).replace(" ","_")].values[i]).replace(";",", "))
                        widget.clicked.connect(self.viewQuote)
                        widget.setObjectName("database-click")
                        if i % 2 == 0:  # Alternate row colors
                            widget.setStyleSheet("QLineEdit{background: " + Alternating_color + "; color: " + Alternating_font + ";}QLineEdit::hover{color:blue;}")
                    else:
                        #widget = QLineEdit(str(df[(database_headers[j]).replace(" ","_")].values[i]).replace(";",", "))
                        widget.setObjectName("database")
                        if i % 2 == 0:  # Alternate row colors
                            widget.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    widget.setAlignment(QtCore.Qt.AlignCenter)
                    self.table_grid.addWidget(widget,i+1,j)

                #make edit and delete toolbutton
                edit = QToolButton()
                edit.setToolTip("Edit")
                edit.setIcon(QIcon("./images/edit button.png"))
                edit.clicked.connect(lambda: self.editQuote())

                delete = QToolButton()
                delete.setToolTip("Delete")
                delete.setIcon(QIcon("./images/delete button.png"))
                delete.clicked.connect(lambda: self.deleteQuote())

                #alternate colors
                if i%2 == 0:
                    edit.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                    delete.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")

                self.table_grid.addWidget(edit,i+1,j+1)
                self.table_grid.addWidget(delete, i+1, j+2)

            for i in large_rows:
                for j in range(len(database_headers)):
                    if type(self.table_grid.itemAtPosition(i + 1, j).widget()) == QLineEdit or type(self.table_grid.itemAtPosition(i + 1, j).widget()) == ClickableLineEdit:
                        self.table_grid.itemAtPosition(i + 1, j).widget().setObjectName("special") #Create special category so not confined by height rules in CSS
                        self.table_grid.itemAtPosition(i + 1, j).widget().setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        except Exception as e:
            print(e,405)


    def onSubmitSearchOLD(self):
        try: #either use panda or pyodbc
            df = pd.read_csv(DATABASE_FILE)
            search_by = self.search_dictionary[self.search_by_box.currentText()]
            search_text = self.search_box.text()
            #print(df[search_by].where(df[search_by] == search_text)) #just gets that one row
            search_result_index = df.index[df[search_by] == search_text].tolist() #Gets indexes
            #TODO: Make sure search result independent of capatilization
            #TODO: search with multiple parts - so see if search_text in and not equal to

            #delete all extra rows in grid
            try:
                for i in range(1,self.table_grid.rowCount()):
                    for j in range(self.table_grid.columnCount()):
                        wid = self.table_grid.itemAtPosition(i,j).widget()
                        self.table_grid.removeWidget(wid)
            except: #Means no extra rows
                pass

            self.insertDatabaseGridOLD(search_result_index,df)

        except Exception as e:
            print(e)


    def insertDatabaseGridOLD(self,search_item,df):
        for i in range(len(search_item)): #Rows in df #TODO: What if multiple part numbers? How display, how put into csv, how search
            for j in range(len(database_headers)): #Col in grid
                widget = QLineEdit(str(df[database_headers[j]][i]))
                widget.setAlignment(QtCore.Qt.AlignCenter)
                widget.setObjectName("database")
                if i%2 == 0: #Alternate row colors
                    widget.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
                self.table_grid.addWidget(widget,i+1,j)
            edit = QToolButton()
            edit.setIcon(QIcon("./images/edit button.png"))
            edit.clicked.connect(lambda: self.editQuote())
            if i%2 == 0:
                edit.setStyleSheet("background: " + Alternating_color + "; color: " + Alternating_font + ";")
            self.table_grid.addWidget(edit,i+1,j+1)

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

            self.insertDatabaseGrid(self.organizeQuote(self.searched_df,text))
        except Exception as e:
            print(e)

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
            print(e)

    def editQuote(self):#TODO: Grab quote from databse when clicked so have most uptodate info
        try:
            btn = self.sender()
            index = self.table_grid.indexOf(btn)
            row = self.table_grid.getItemPosition(index)[0] - 1

            if main_window.tabs.widget(1).invoice_number.text() == str(self.searched_df["Quote_Number"].values[row]):
                main_window.tabs.setCurrentIndex(1)  # switch to active quote tab
            elif main_window.tabs.widget(1).invoice_number.text() != "":
                action = self.sendQuoteInUseMsg()

                if action == QMessageBox.Yes:
                    main_window.tabs.widget(1).submitQuote()
                    self.continueEditQuote(row)
                if action == QMessageBox.No:
                    self.continueEditQuote(row)
            else:
                self.continueEditQuote(row)
        except Exception as e:
            print(e)

    #Where the quote is put onto the GUI
    def continueEditQuote(self,row):
        try:
            #Clears anything in activequote tab
            main_window.tabs.removeTab(1)
            main_window.tabs.insertTab(1,ActiveQuote(),"Active Quote") #TODO: add dialog box if quote being edited
            main_window.tabs.setCurrentIndex(1) #switch to active quote tab

            quote = main_window.tabs.widget(1)
            df = self.searched_df

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
                    quote.table.itemAt(i).layout().itemAt(2).widget().setText(quantity)
                except:
                    pass
                try:
                    quote.table.itemAt(i).layout().itemAt(3).widget().setText(part_numbers[i - 1])
                except:
                    pass
                try:
                    quote.table.itemAt(i).layout().itemAt(4).widget().setText(conditions[i - 1])
                except:
                    pass
                try:
                    unit_price = unit_prices[i - 1]
                    if unit_price == "None":
                        unit_price = '0'
                    quote.table.itemAt(i).layout().itemAt(5).widget().setText(unit_price)
                except:
                    pass
                try:
                    line_total = line_totals[i - 1]
                    if line_total == "None":
                        line_total = '0'
                    quote.table.itemAt(i).layout().itemAt(6).widget().setText(line_total)
                except:
                    pass
                try:
                    quote.table.itemAt(i).layout().itemAt(7).widget().setText(stocks[i - 1])
                except:
                    pass
                try:
                    quote.table.itemAt(i).layout().itemAt(8).widget().setText(notes[i - 1])
                except:
                    pass


            quote.invoice_number.setText(str(df["Quote_Number"].values[row]))

            quote.sent_from.setCurrentText(str(df["Sender"].values[row]))

            quote.customer_name.setText(str(df["Customer_Name"].values[row]))

            quote.customer_email.setText(str(df["Customer_Email"].values[row]))

            quote.customer_phone.setText(str(df["Customer_Phone"].values[row]))

            quote.customer_info.setText(str(df["Customer_Notes"].values[row]))

            quote.payment_terms.setCurrentText(str(df["Payment_Terms"].values[row]))

            quote.shipping_method.setCurrentText(str(df["Shipping_Method"].values[row]))

            quote.shipping_charges.setText(str(df["Shipping_Charges"].values[row]))

            additional_notes = str(df["Additional_Notes"].values[row])
            quote.additional_infos.setText(additional_notes)
            for i in range(main_window.tabs.widget(1).note_group_grid.count()):
                widget = main_window.tabs.widget(1).note_group_grid.itemAt(i).widget()
                if widget.text() in additional_notes:
                    widget.setChecked(True)

            #TODO: When add back in, check checkboxes if applicable
        except Exception as e:
            print(e)


    def deleteQuote(self): #TODO: Delete from df and refresh so not show
        btn = self.sender()
        index = self.table_grid.indexOf(btn)
        row = self.table_grid.getItemPosition(index)[0] - 1

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Delete Quote")
        msg.setText("Are you sure you want to delete the quote? This action is not undoable.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        action = msg.exec()

        if action == QMessageBox.Yes:
            deleteQuote(str(self.searched_df["Quote_Number"].values[row]))



    def newQuote(self):
        if main_window.tabs.widget(1).invoice_number.text() != "":
            action = self.sendQuoteInUseMsg()

            if action == QMessageBox.Yes:
                main_window.tabs.widget(1).submitQuote()
                self.continueNewQuote()
            if action == QMessageBox.No:
                self.continueNewQuote()
        else:
            self.continueNewQuote()

    def continueNewQuote(self):
        #Clears activequote tab and inserts new
        main_window.tabs.removeTab(1)
        main_window.tabs.insertTab(1, ActiveQuote(), "Active Quote")  # TODO: add dialog box if quote being edited
        main_window.tabs.setCurrentIndex(1)  # switch to active quote tab

        main_window.tabs.setCurrentIndex(1)
        main_window.tabs.widget(1).invoice_number.setText(getNewInvoiceNumber())

    def viewQuote(self):
        try:
            btn = self.sender()
            quote_number = btn.text()

            df = self.searched_df.loc[self.searched_df['Quote_Number'] == quote_number]
            #html = getHTMLText(["CQM1-OC222", "CQM1-AD042"], [1, 2], ["New", "Used"], [1240, 1000], [1240, 2000],
                               #["In Stock", "20 Day lead time"],
                               #"Kristopher Stickney", "kstickney@trwsupply.com", "082221-12051", "k@gmail.com",
                               #"RFQ Parts",
                               #"08/22/2021",
                               #"Credit Card", "UPS", ["New - 1 year warranty", "No warranty"])

            html = getViewHTMLText(str(df["Part_Number"].values[0]).split(';'),str(df["Quantity"].values[0]).split(';'),str(df["Condition"].values[0]).split(';'),
                               str(df["Unit_Price"].values[0]).split(';'),str(df["Line_Total"].values[0]).split(';'),
                               str(df["Stock"].values[0]).split(';'),
                               str(df["Sender"].values[0]),str(df["Sender_Email"].values[0]),
                               str(df["Quote_Number"].values[0]),str(df["Customer_Email"].values[0]),
                               str(df["Subject"].values[0]),str(df["_Date"].values[0]),str(df["Payment_Terms"].values[0]),
                               str(df["Shipping_Method"].values[0]),str(df["Additional_Notes"].values[0]).split("\n"))
            main_window.tabs.setCurrentIndex(2)
            main_window.tabs.widget(2).addTabPage(html, quote_number)

        except Exception as e:
            print(e,1187)

    def sendQuoteInUseMsg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Quote Already Started")
        msg.setText("There is a quote already started. Do you wish to save?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        # msg.buttonClicked.connect(self.continueEdit)

        action = msg.exec()

        return action

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
        global THEME
        THEME = text

        text = text.lower()

        if "classic" in text:
            styleSheet = './styles/classic/style.qss'
        elif "orange" in text:
            styleSheet = './styles/dark_orange/style.qss'
        elif "blue" in text:
            styleSheet = './styles/dark_blue/style.qss'  # Had to change ":/" for files to "./"
        elif "dark" == text:
            styleSheet = './styles/dark/style.qss'
        elif "light" == text:
            styleSheet = './styles/light/style.qss'
        else:
            styleSheet = './styles/dark_orange/style.qss'

        with open(styleSheet, "r") as fh:
            app.setStyleSheet(fh.read())

        Alternating_color = ALTERNATING_COLORS[text][0]
        Alternating_font = ALTERNATING_COLORS[text][1]

    except Exception as e:
        print(e)

def storeSettings():
    new_settings = {
        "Payment Terms": PAYMENT_TERMS,
        "Shipping Methods": SHIPPING_METHODS,
        "Table Headers": table_headers,
        "Initial Part Rows": INITIAL_PART_ROWS,
        "Database Headers": database_headers,
        "Sample Notes": sample_notes,
        "Senders": senders,
        "Preferred Search": preferred_search,
        "Theme": THEME,
        "Alternating Color": Alternating_color,
        "Alternating Font": Alternating_font,
    }

    # Store data (serialize)
    with open(settings_file, 'wb') as handle:
        pickle.dump(new_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)



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
    msg.exec_()

class Error(QMainWindow):
    pass

class Found(Exception):
    pass

def exit_app():
    closeSQLConnection()



if __name__ == '__main__':
    try:

        # Store data (serialize)
        #with open(settings_file, 'wb') as handle:
            #pickle.dump(default_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
            #print("Default Settings Stored")

        #error = Error()

        # Load data (deserialize)
        try:
            with open(settings_file, 'rb') as handle:
                settings = pickle.load(handle)
            #print(1/0)

        except Exception as e:
            sendMessage("Error", "Error loading settings", parent=error, type = QMessageBox.Critical)

        # Load settings into respective variables
        try:
            PAYMENT_TERMS = settings["Payment Terms"]
            SHIPPING_METHODS = settings["Shipping Methods"]
        except Exception as e:
            PAYMENT_TERMS = default_payment_terms
            SHIPPING_METHODS = default_shipping_methods
        try:
            table_headers = settings["Table Headers"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            table_headers = default_table_headers
        try:
            INITIAL_PART_ROWS = settings["Initial Part Rows"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            INITIAL_PART_ROWS = default_initial_part_rows
        try:
            database_headers = settings["Database Headers"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            database_headers = default_database_headers
        try:
            sample_notes = settings["Sample Notes"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            sample_notes = default_sample_notes
        try:
            senders = settings["Senders"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            senders = default_senders
        try:
            preferred_search = settings["Preferred Search"]
        except Exception as e:
            sendMessage("Error", "Cannot load preference. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            preferred_search = default_preferred_search
        try:
            THEME = settings["Theme"]
            Alternating_color = settings["Alternating Color"]
            Alternating_font = settings["Alternating Font"]
        except Exception as e:
            sendMessage("Error", "Cannot load saved theme. Default Settings Loaded", parent=error, type = QMessageBox.Critical)
            THEME = default_theme
            Alternating_color = default_alternating_color
            Alternating_font = default_alternating_font

        # app = QApplication([])
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(exit_app)
        setTheme(THEME)
        app.setStyle('Fusion')
        df = getQuote("")
        DATABASE_HEADERS = list(df.columns)
        main_window = MainWindow()
        sys.exit(app.exec_())

    except Exception as e:
        print(e)



