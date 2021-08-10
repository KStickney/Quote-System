import pyodbc
import pandas as pd
#Either use pandas or pyodbc. Pandas just for reading, pyodbc for editing (and reading)
#https://pythoninoffice.com/how-to-connect-and-work-with-ms-access-database-using-python-pyodbc/

database_file = "./TRW Supply Item Database 1.3.7 (192.168.0.2).accdb"

conn = pyodbc.connect(
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+database_file+';')
cursor = conn.cursor()
cursor.execute('select * from Item_Prices')


#for row in cursor.fetchall():
    #print(row)

#df = pd.read_sql('select * from Item_Prices',conn)
#print(df)
