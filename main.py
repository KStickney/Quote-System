#Settings: Allow how many columns, what size each column, if combobox or pure plugin, if and where completer draw from
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math
import pandas as pd
import pickle

from CustomClasses import *


def sendMessage(title,message,type = QMessageBox.Warning): #TODO: Not working if not in a Widget class
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(type)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

#Default Settings
default_payment_terms = {"Credit Card":"CC","NET 30":"NET 30","NET 60":"NET 60","Wire Transfer":"TT"}
default_shipping_methods = ["UPS Ground","UPS NDA","UPS 2nd NDA","FedEx Ground","FedEx NDA","DLH"]
default_table_headers = ["Item","Quantity", "Part Number","Condition","Unit Price","Line Total","Stock","Notes"]
default_initial_part_rows = 3 #How many rows show initially in quote
default_database_headers = ["Quote Number","Customer","Part Number",]
default_sample_notes = ["New Warranty -- 1 year", "Refurbished Warranty -- 1 year","*****************************"]
default_senders = {"Kyle Stickney":"kyle@trwelectric.om",
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

        self.styleSheet = "./Main Stylesheet.css"
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

        self.setCentralWidget(self.tabs)

class ActiveQuote(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = "./Quote Stylesheet.css"
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
        for label in (p,s):
            label.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignRight)
            label.setObjectName("shipping")

        self.payment_terms = QComboBox()
        self.payment_terms.setEditable(False)
        self.payment_terms.addItems(PAYMENT_TERMS.keys())

        self.shipping_method = QComboBox()
        self.shipping_method.setEditable(False)
        self.shipping_method.addItems(SHIPPING_METHODS)

        lay1 = QHBoxLayout()
        lay1.addWidget(p)
        lay1.addWidget(self.payment_terms)

        lay2 = QHBoxLayout()
        lay2.addWidget(s)
        lay2.addWidget(self.shipping_method)

        shipping_layout = QHBoxLayout()
        shipping_layout.addLayout(lay1)
        shipping_layout.addLayout(lay2)


        #Where table grid used to be
        #ITEM TABLE
        self.add_table_item_btn = QPushButton("Add Item")
        self.add_table_item_btn.setObjectName("add-item")
        self.add_table_item_btn.clicked.connect(lambda: self.add_table_item(None,True))

        self.del_table_item_btn = QPushButton("Delete Item")
        self.del_table_item_btn.setObjectName("add-item")
        self.del_table_item_btn.clicked.connect(lambda: self.deleteTableItem())

        self.add_note_btn = QCheckBox("Add Note")
        self.add_note_btn.setObjectName("add-item")
        self.add_note_btn.toggled.connect(lambda: self.addNoteCol())
        self.add_note_btn.setChecked(False)

        self.table = QGridLayout()
        self.table.setSpacing(0)
        self.table.setAlignment(QtCore.Qt.AlignCenter)
        for i in range(INITIAL_PART_ROWS):
            self.add_table_item(i)
        self.addNoteCol()

        self.table_buttons = [self.add_table_item_btn,self.del_table_item_btn,self.add_note_btn]
        i = INITIAL_PART_ROWS + 1
        self.addTableButtons(i)


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
            box.stateChanged.connect(lambda:self.note_checkbox_state())
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
        self.save_and_exit_btn = QPushButton("Save and Close")
        self.close_btn = QPushButton("Close")
        self.submit_layout = QHBoxLayout()
        for btn in (self.save_btn,self.save_and_exit_btn,self.close_btn):
            self.submit_layout.addWidget(btn)
            btn.setObjectName("submit")

        t = CustomGridLayout()
        t.addWidget(QLabel("HI"),0,0)
        t.insertRow(0)

        #MAIN LAYOUT
        self.main_layout = QVBoxLayout() #The main layout for the quote part of the app
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.invoice_layout)
        self.main_layout.addLayout(self.table) #TODO: Fix spacing, table taking up extra space
        self.main_layout.addLayout(self.customer_layout)
        self.main_layout.addLayout(shipping_layout)
        self.main_layout.addLayout(self.additional_info_out_layout)
        self.main_layout.addLayout(self.submit_layout)
        self.main_layout.addLayout(t)

        self.scroll_area = QScrollArea() #Allows app to scroll
        self.scroll_area.setLayout(self.main_layout)
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

                if i % 2 == 1:
                    cell.setStyleSheet("background: "+Alternating_color+"; color: "+Alternating_font+";")

                if i == 0: #Means Header
                    cell.setReadOnly(True)
                    cell.setObjectName("table-header")
                    cell.setText(table_headers[j])
                else:
                    if table_headers[j] == "Part Number":
                        cell.setValidator(Validator())
                    cell.setCompleter(completer)
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

    def addTableButtons(self,i):
        for j in range(len(self.table_buttons)):
            v = QHBoxLayout()
            v.addWidget(self.table_buttons[j])
            v.setStretch(1,0)
            #self.table.addWidget(self.table_buttons[j],i,j+1)
            self.table.addItem(v,i,j+1)
        self.table_row_count+=1

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

    def deleteTableItem(self): #TODO: Fix mashup delete
        try:
            rows = self.checkTableCheckboxes()
            for i in rows:
                for j in range(self.table.columnCount()):
                    try:
                        self.table.removeWidget(self.table.itemAtPosition(i,j).widget())
                    except:
                        pass
                self.table_row_count -= 1
        except Exception as e:
            print(e)


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



class ViewQuotes(QWidget):
    def __init__(self):
        super().__init__()

        self.UIComponents()

    def UIComponents(self):
        self.dock_widget = QDockWidget("Active Quotes")
        self.dock_widget.setWidget(QTabWidget())

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.dock_widget)
        self.setLayout(self.main_layout)


class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.styleSheet = "./Settings Stylesheet.css"
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

    def submitHeaders(self): #TODO: Update database tab
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
        wid.setCurrentText(header)
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

        self.styleSheet = "./Database Stylesheet.css"
        with open(self.styleSheet, "r") as fh:
            self.setStyleSheet(fh.read())

        self.UIComponents()

    def UIComponents(self):
        self.new_quote_btn = QPushButton("New Quote")

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
        for j in range(len(database_headers)): #TODO: Change part column (or any with multiple lines) with QTextEdit
            wid = QLineEdit(database_headers[j])
            wid.setReadOnly(True)
            wid.setAlignment(QtCore.Qt.AlignCenter)
            wid.setObjectName("database-header")
            self.table_grid.addWidget(wid,0,j)

        #OPENS DATABASE and reads as a pandas dataframe and inserts into grid
        df = pd.read_csv(DATABASE_FILE)
        self.insertDatabaseGrid(df, df)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.search_layer)
        self.main_layout.addLayout(self.table_grid)
        self.setLayout(self.main_layout)

    def addComboOptions(self, box):
        self.search_dictionary = {}
        for search in database_headers:
            self.search_dictionary["Search by " + search.lower()] = search
            # self.search_by_box.addItem("Search by "+search.lower())
        box.addItems(self.search_dictionary.keys())
        for i in range(box.count()):
            if preferred_search.lower() in box.itemText(i).lower():
                box.setCurrentText(box.itemText(i))

    def onSubmitSearch(self):
        try:
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

            self.insertDatabaseGrid(search_result_index,df)

        except Exception as e:
            print(e)


    def insertDatabaseGrid(self,search_item,df):
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

    def editQuote(self):
        btn = self.sender()
        index = self.table_grid.indexOf(btn)

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


if __name__ == '__main__':
    # Store data (serialize)
    #with open(settings_file, 'wb') as handle:
        #pickle.dump(default_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #print("Default Settings Stored")

    # Load data (deserialize)
    try:
        with open(settings_file, 'rb') as handle:
            settings = pickle.load(handle)

    except Exception as e:
        sendMessage("Error", "Error loading settings", QMessageBox.Critical)

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
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        table_headers = default_table_headers
    try:
        INITIAL_PART_ROWS = settings["Initial Part Rows"]
    except Exception as e:
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        INITIAL_PART_ROWS = default_initial_part_rows
    try:
        database_headers = settings["Database Headers"]
    except Exception as e:
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        database_headers = default_database_headers
    try:
        sample_notes = settings["Sample Notes"]
    except Exception as e:
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        sample_notes = default_sample_notes
    try:
        senders = settings["Senders"]
    except Exception as e:
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        senders = default_senders
    try:
        preferred_search = settings["Preferred Search"]
    except Exception as e:
        sendMessage("Error", "Cannot load preference. Default Settings Loaded", QMessageBox.Critical)
        preferred_search = default_preferred_search
    try:
        THEME = settings["Theme"]
        Alternating_color = settings["Alternating Color"]
        Alternating_font = settings["Alternating Font"]
    except Exception as e:
        sendMessage("Error", "Cannot load saved theme. Default Settings Loaded", QMessageBox.Critical)
        THEME = default_theme
        Alternating_color = default_alternating_color
        Alternating_font = default_alternating_font

    #app = QApplication([])
    app = QApplication(sys.argv)
    setTheme(THEME)
    app.setStyle('Fusion')
    df = pd.read_csv(DATABASE_FILE)
    DATABASE_HEADERS = list(df.columns)
    main_window = MainWindow()
    sys.exit(app.exec_())



