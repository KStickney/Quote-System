import pyodbc
import pandas as pd

database_file = "./data/TRW Quote Database.accdb"
part_number_table = 'Part_Numbers'

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+database_file+';')
cursor = conn.cursor()

def getPartNumbers():
    part_numbers = []

    cursor.execute('select * from '+part_number_table)
    for row in cursor.fetchall():
        part_numbers.append(row[0].upper())

    return part_numbers
