import pyodbc
import pandas as pd
from datetime import date

database_file = "./data/TRW Quote Database.accdb"
part_number_table = 'Part_Numbers'
quote_table = 'Quotes'

QUOTE_STARTING_NUMBER = '00000'

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+database_file+';')
cursor = conn.cursor()

def getQuotes(): #Returns all quotes, mainly used for searching
    try:

        cursor.execute('select * from ' + quote_table)

        #index = cursor.fetchall().index('81721-00001',0,4) what do??

        return cursor

    except Exception as e:
        print(e)

def getPartNumbers():
    part_numbers = []

    cursor.execute('select Part_Number from '+part_number_table)
    for row in cursor.fetchall():
        part_numbers.append(row[0].upper())

    return part_numbers

def getInvoiceNumber():

    cursor.execute('select Quote_Number from ' + quote_table)

    last = int(cursor.fetchall()[0][0][6:11])#TODO: change first [] to either 0 or len() depending on if append new quotes to beginning or end

    today = date.today()

    invoice = str(today.month) + str(today.day) + str(today.strftime('%y')) + "-" + str(last+1).zfill(5)

    return invoice
