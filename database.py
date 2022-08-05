import pyodbc
import pandas as pd
from datetime import date, datetime
import pickle, os

# database_settings_file = "./data/database.pickle"
##database_settings_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/database.pickle")

# Store data (serialize)
# with open(database_settings_file, 'wb') as handle:
# pickle.dump(database_settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
# print("Default Settings Stored")

##with open(database_settings_file, 'rb') as handle:
##database_settings = pickle.load(handle)

# database_file = "./data/TRW Quote Database.accdb"
##database_file = database_settings["Database Path"]

part_number_table = "Part_Numbers"
quote_table = "Quotes"
variable_table = "Variables"

QUOTE_STARTING_NUMBER = "12000"

global connection
global cursor

# TODO: if can't find database, setup new one
def connectDatabase(database_file):
    # global connection, cursor
    global connection
    global cursor

    try:
        connection = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ="
            + database_file
            + ";"
        )

        # connection = pyodbc.connect(r'DSN=MSSQL-PYTHON;DRIVER={SQL Server};DBQ='+database_file+';')
        cursor = connection.cursor()
    except Exception as e:
        try:
            print(e)
            connection = pyodbc.connect(
                r"Driver={SQL Server};DBQ=" + database_file + ";"
            )
            cursor = connection.cursor()
        except Exception as e:
            print(e)
            try:
                connection = pyodbc.connect(
                    r"Driver={SQL Server};server='MS Access Database';DBQ="
                    + database_file
                    + ";"
                )
                cursor = connection.cursor()
            except Exception as e:
                print(e)
                connection = pyodbc.connect(
                    r"Driver={SQL Server};server='MS Access Database';DBQ="
                    + database_file
                    + ";Trusted_Connection=yes;"
                )
                cursor = connection.cursor()


def closeDatabaseConnection():
    global connection
    connection.close()


# Get current date and time
# today = datetime.now()
# Convert string into datetime object for comparosin
# date = datetime.strptime(string,'%Y-%m-%d %H:%M:%S.%f')


# sql="Insert into Quotes (Quote_Number, Part_Number, Price) values ('8117-00004', 'CQM1-OC222','27')"
# cursor.execute(sql)
# connection.commit()


def getQuoteLastEdited(quote_number):
    df = pd.read_sql(
        f"Select Last_Edited from {quote_table} WHERE Quote_Number = '{quote_number}'",
        connection,
    )
    return datetime.strptime(str(df.iloc[0][0]), "%Y-%m-%d %H:%M:%S.%f")


def getQuotes1(search, search_by):
    try:
        search = search.lower()
        df = pd.read_sql(
            f"Select * from {quote_table} WHERE {search_by} LIKE '%{search}%'",
            connection,
        )

        return df
    except Exception as e:
        print(e)


def getQuotes2(search1, search2, search_by1, search_by2):
    try:
        search1 = search1.lower()
        search2 = search2.lower()
        df = pd.read_sql(
            "Select * from "
            + quote_table
            + f" WHERE {search_by1} LIKE '%{search1}%' AND {search_by2} LIKE '%{search2}%' ",
            connection,
        )

        return df
    except Exception as e:
        print(e)


def getQuotes3(search1, search2, search3, search_by1, search_by2, search_by3):

    df = pd.read_sql(
        "Select * from "
        + quote_table
        + f" WHERE {search_by1} LIKE '%{search1}%' AND {search_by2} LIKE '%{search2}%' AND {search_by3} LIKE '%{search3}%' ",
        connection,
    )

    return df


def getQuotes():  # Returns all quotes, mainly used for searching
    try:

        # cursor.execute('select * from ' + quote_table)

        # index = cursor.fetchall().index('81721-00001',0,4) what do??

        # return cursor

        df = pd.read_sql("select * from " + quote_table, connection)

        return df

    except Exception as e:
        print(e)


def getQuote(id):

    df = pd.read_sql(
        f"SELECT * from {quote_table} WHERE Quote_Number = '{id}'", connection
    )
    return df


def getPartNumbers():
    part_numbers = []

    cursor.execute("select Part_Number from " + part_number_table)
    for row in cursor.fetchall():
        part_numbers.append(row[0].upper())

    return part_numbers


def updatePartNumbers(parts_list):
    try:
        ##adds new in Part_Numbers table in database
        for part in parts_list:

            # Check see if part already in database
            cursor.execute(
                f"SELECT Part_Number from {part_number_table} where Part_Number=?", part
            )
            data = cursor.fetchall()

            if not data:  # part not found in database, so add part to list
                cursor.execute(
                    f"INSERT into {part_number_table} (Part_Number) values ('{part}')"
                )

        connection.commit()
    except Exception as e:
        print(e)


def getNewInvoiceNumber():

    cursor.execute("select Quote_Number from " + variable_table)

    last = int(cursor.fetchall()[0][0])
    new = str(last + 1).zfill(5)

    today = date.today()

    invoice = (
        str(today.month).zfill(2)
        + str(today.day).zfill(2)
        + str(today.strftime("%y"))
        + "-"
        + new
    )

    # update field with latest quote number
    updateInvoiceNumber(new)

    return invoice


def updateInvoiceNumber(num):

    old = str(int(num) - 1).zfill(5)

    cursor.execute(
        f"UPDATE {variable_table} SET Quote_Number =  '{num}' WHERE Quote_Number = '{old}'"
    )

    connection.commit()


def submitNewQuoteToDatabase(quote_number):
    global connection, cursor
    Date = date.today().strftime("%m/%d/%Y")
    sql = f"INSERT into {quote_table} (Quote_Number,_Date,isEditing) values ('{quote_number}','{Date}',TRUE)"
    cursor.execute(sql)
    connection.commit()
    print("New Quote Saved")


def submitQuoteToDatabase(
    quote_number,
    quantities,
    part_numbers,
    conditions,
    unit_prices,
    line_totals,
    stock,
    notes,
    subject,
    sender,
    sender_email,
    customer_name,
    customer_email,
    customer_phone,
    customer_notes,
    additional_notes,
    payment_terms,
    shipping_method,
    shipping_charges,
    pro_forma,
    last_edited,
):

    cursor.execute(
        "select Quote_Number from Quotes where Quote_Number=?", quote_number
    )  # checking see if already exists
    data = cursor.fetchall()

    # last_edited = str(datetime.now())
    last_edited = str(last_edited)

    if not data:  # None found, so can insert new line
        Date = date.today().strftime("%m/%d/%Y")
        sql = (
            f"Insert into Quotes (Quote_Number, Quantity, Part_Number, Condition, Unit_Price, Line_Total, Stock, Notes,"
            "Subject,Sender,Sender_Email, Customer_Name, Customer_Email, Customer_Phone, Customer_Notes, Additional_Notes, Payment_Terms,"
            "Shipping_Method, Shipping_Charges,_Date,Pro_Forma,Last_Edited) "
            f"values ('{quote_number}', '{quantities}','{part_numbers}','{conditions}','{unit_prices}','{line_totals}',"
            f"'{stock}','{notes}','{subject}','{sender}','{sender_email}','{customer_name}','{customer_email}','{customer_phone}','{customer_notes}',"
            f"'{additional_notes}','{payment_terms}','{shipping_method}','{shipping_charges}','{Date}',{pro_forma},'{last_edited}')"
        )

        cursor.execute(sql)

    else:  # entry found, update instead (Completely updates - deletes and puts in)

        cursor.execute(
            "UPDATE "
            + quote_table
            + " SET Quantity=?,Part_Number=?,Condition=?,Unit_Price=?,Line_Total=?,"
            "Stock=?,Notes=?,Subject=?,Sender=?,Sender_Email=?,Customer_Name=?,Customer_Email=?,Customer_Phone=?,Customer_Notes=?,"
            "Additional_Notes=?,Payment_Terms=?,Shipping_Method=?,Shipping_Charges=?,Pro_Forma=?,Last_Edited=? WHERE Quote_Number=?",
            (
                quantities,
                part_numbers,
                conditions,
                unit_prices,
                line_totals,
                stock,
                notes,
                subject,
                sender,
                sender_email,
                customer_name,
                customer_email,
                customer_phone,
                customer_notes,
                additional_notes,
                payment_terms,
                shipping_method,
                shipping_charges,
                pro_forma,
                last_edited,
                quote_number,
            ),
        )

    connection.commit()
    print("Quote Saved")


def updateIsEditing(quote_number, isEditing):
    try:
        cursor.execute(
            f"UPDATE {quote_table} SET isEditing= {isEditing} WHERE Quote_Number='{quote_number}'"
        )
        cursor.commit()
    except Exception as e:
        print(e)


def deleteQuote(id):
    cursor.execute(f"DELETE FROM {quote_table} WHERE Quote_Number = '{id}'")
    cursor.commit()
    print("Quote Deleted")


def closeSQLConnection():
    global connection
    connection.close()
    print("Connection Closed")


def getYLNewPrice(part):
    df = pd.read_sql(
        f"Select YL_New_Price from {part_number_table} WHERE Part_Number LIKE '%{part}%'",
        connection,
    )
    return df


def getYLRefPrice(part):
    df = pd.read_sql(
        f"Select YL_Ref_Price from {part_number_table} WHERE Part_Number LIKE '%{part}%'",
        connection,
    )
    return df


def getMFRPrice(part):
    df = pd.read_sql(
        f"Select Manufacturer_Price from {part_number_table} WHERE Part_Number LIKE '%{part}%'",
        connection,
    )
    return df
