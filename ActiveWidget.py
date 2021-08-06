from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

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


        #MAIN LAYOUT
        self.main_layout = QVBoxLayout() #The main layout for the quote part of the app
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.invoice_layout)
        self.main_layout.addLayout(self.table) #TODO: Fix spacing, table taking up extra space
        self.main_layout.addLayout(self.customer_layout)
        self.main_layout.addLayout(shipping_layout)
        self.main_layout.addLayout(self.additional_info_out_layout)
        self.main_layout.addLayout(self.submit_layout)

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
                cell.setCompleter(completer)
                cell.setAlignment(QtCore.Qt.AlignCenter)
                cell.setObjectName("table")
                if i % 2 == 1:
                    cell.setStyleSheet("background: "+Alternating_color+"; color: "+Alternating_font+";")
                if j == 0:
                    cell.setFixedWidth(100)
                if i == 0:
                    cell.setReadOnly(True)
                    cell.setObjectName("table-header")
                    cell.setText(table_headers[j])
                if j == (len(table_headers)-1) and not self.add_note_btn.isChecked():
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
                    self.table.removeWidget(self.table.itemAtPosition(i,j).widget())
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