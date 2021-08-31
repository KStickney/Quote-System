import pyodbc
import pandas as pd
from datetime import date
import pickle

database_settings_file = "./data/database.pickle"

# Store data (serialize)
#with open(database_settings_file, 'wb') as handle:
    #pickle.dump(database_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #print("Default Settings Stored")

with open(database_settings_file, 'rb') as handle:
    database_settings = pickle.load(handle)

#database_file = "./data/TRW Quote Database.accdb"
database_file = database_settings["Database Path"]
part_number_table = 'Part_Numbers'
quote_table = 'Quotes'
variable_table = 'Variables'

QUOTE_STARTING_NUMBER = '12000'

#TODO: if can't find database, setup new one
connection = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+database_file+';')
cursor = connection.cursor()

#sql="Insert into Quotes (Quote_Number, Part_Number, Price) values ('8117-00004', 'CQM1-OC222','27')"
#cursor.execute(sql)
#connection.commit()


def getQuotes1(search,search_by):
    try:
        search = search.lower()
        df = pd.read_sql(f"Select * from {quote_table} WHERE {search_by} LIKE '%{search}%'",connection)

        return df
    except Exception as e:
        print(e)

def getQuotes2(search1,search2,search_by1,search_by2):
    try:
        search1 = search1.lower()
        search2 = search2.lower()
        df = pd.read_sql("Select * from " + quote_table + f" WHERE {search_by1} LIKE '%{search1}%' AND {search_by2} LIKE '%{search2}%' ",connection)

        return df
    except Exception as e:
        print(e)

def getQuotes(): #Returns all quotes, mainly used for searching
    try:

        #cursor.execute('select * from ' + quote_table)

        #index = cursor.fetchall().index('81721-00001',0,4) what do??

        #return cursor

        df = pd.read_sql('select * from ' + quote_table, connection)

        return df

    except Exception as e:
        print(e)

def getQuote(id):

    df = pd.read_sql(f"SELECT * from {quote_table} WHERE Quote_Number = '{id}'",connection)
    return df

def getPartNumbers():
    part_numbers = []

    cursor.execute('select Part_Number from '+part_number_table)
    for row in cursor.fetchall():
        part_numbers.append(row[0].upper())

    return part_numbers

def getNewInvoiceNumber():

    cursor.execute('select Quote_Number from ' + variable_table)

    last = int(cursor.fetchall()[0][0])
    new = str(last+1).zfill(5)

    today = date.today()

    invoice = str(today.month).zfill(2) + str(today.day) + str(today.strftime('%y')) + "-" + new

    #update field with latest quote number
    updateInvoiceNumber(new)

    return invoice

def updateInvoiceNumber(num):

    old = str(int(num)-1).zfill(5)

    cursor.execute(f"UPDATE {variable_table} SET Quote_Number =  '{num}' WHERE Quote_Number = '{old}'")

    connection.commit()

def submitQuoteToDatabase(quote_number,quantities,part_numbers,conditions,unit_prices,line_totals,stock,notes,sender,sender_email,
                          customer_name,customer_email,customer_phone,customer_notes,additional_notes,payment_terms,
                          shipping_method,shipping_charges,pro_forma):
    cursor.execute("select Quote_Number from Quotes where Quote_Number = ?",quote_number) #checking see if already exists
    data = cursor.fetchall()

    if not data: #None found, so can insert new line
        Date = date.today().strftime("%m/%d/%Y")
        sql=f"Insert into Quotes (Quote_Number, Quantity, Part_Number, Condition, Unit_Price, Line_Total, Stock, Notes," \
            "Sender,Sender_Email, Customer_Name, Customer_Email, Customer_Phone, Customer_Notes, Additional_Notes, Payment_Terms," \
            "Shipping_Method, Shipping_Charges,_Date,Pro_Forma) " \
            f"values ('{quote_number}', '{quantities}','{part_numbers}','{conditions}','{unit_prices}','{line_totals}'," \
            f"'{stock}','{notes}','{sender}','{sender_email}','{customer_name}','{customer_email}','{customer_phone}','{customer_notes}'," \
            f"'{additional_notes}','{payment_terms}','{shipping_method}','{shipping_charges}','{Date}','{pro_forma}')"

        cursor.execute(sql)

    else: #entry found, update instead (Completely updates - deletes and puts in)

        cursor.execute("UPDATE " + quote_table + " SET Quantity=?,Part_Number=?,Condition=?,Unit_Price=?,Line_Total=?," \
                        "Stock=?,Notes=?,Sender=?,Sender_Email=?,Customer_Name=?,Customer_Email=?,Customer_Phone=?,Customer_Notes=?," \
                        "Additional_Notes=?,Payment_Terms=?,Shipping_Method=?,Shipping_Charges=?,Pro_Forma=? WHERE Quote_Number=?",
                       (quantities, part_numbers, conditions, unit_prices, line_totals, stock, notes, sender,sender_email,
                        customer_name, customer_email, customer_phone, customer_notes, additional_notes, payment_terms,
                        shipping_method, shipping_charges,pro_forma, quote_number))


    connection.commit()
    print("Quote Saved")

def updateIsEditing(quote_number, isEditing):
    try:
        cursor.execute(f"UPDATE {quote_table} SET isEditing= {isEditing} WHERE Quote_Number='{quote_number}'")
        cursor.commit()
    except Exception as e:
        print(e)


def deleteQuote(id):
    print(id)
    cursor.execute(f"DELETE FROM {quote_table} WHERE Quote_Number = '{id}'")
    cursor.commit()
    print("Quote Deleted")

def closeSQLConnection():
    connection.close()

