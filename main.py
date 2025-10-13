import csv
import sys

#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasgui
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pywin32
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install xlrd
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasql

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import pandas.io.sql as psql
import pandasql as ps

from IPython.core.display_functions import display
from pandas.compat import numpy
from pandas.io.formats import string

from pandasgui import show

import psycopg2
from sqlalchemy import create_engine
import xlrd

#import pywin32
import win32api

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    #df1 = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
    #show(df1)
    #print(df1.compare(df1))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)

    #with open("C:\\Users\\jesus.ordonez\\bitbucket\\misc\\PASAY\\All_Patinio - Detailed Account Transaction Report - Clean.csv", 'r') as reader:
        #CSVfh = csv.reader(reader)
        #print(type(CSVfh))
        #CSVl = list(CSVfh)


    #dataFrameCSV = pd.read_csv("C:\\Users\\jesus.ordonez\\bitbucket\\misc\\PASAY\\All_Patinio - Detailed Account Transaction Report - Clean.csv")
   # dataFrameCSV = pd.read_excel("C:\\Users\\jesus.ordonez\\bitbucket\\misc\\PASAY\\All_Patinio - Detailed Account Transaction Report.xls")
    dataFrameCSV = pd.read_excel("C:\\Users\\jesus.ordonez\\bitbucket\\misc\\PASAY\\Patinio - Detailed Account Transaction Report122822.xls")

    # print(dataFrameCSV)
    #dataFrameCSV = dataFrameCSV.astype(str)

    #    {'trans_gross': 'string', 'trans_tax': 'string', 'trans_net': 'string', 'trans_tax_rate': 'string'})
    dataFrameCSV = dataFrameCSV.drop([dataFrameCSV.index[0], dataFrameCSV.index[1], dataFrameCSV.index[2],dataFrameCSV.index[3063]])

    #res = dataFrameCSV.drop(1)
    #res = dataFrameCSV.drop(2)

    dataFrameCSV.columns = [
        "acct_code",
        "acct_name",
        "trans_date",
        "trans_type",
        "trans_des",
        "trans_ref",
        "trans_gross",
        "trans_tax",
        "trans_net",
        "trans_tax_rate",
        "trans_tax_name",
    ]

    dataFrameCSV.head()

    #dataFrameCSV = dataFrameCSV.astype(str)
    # {'trans_gross': 'string', 'trans_tax': 'string', 'trans_net': 'string', 'trans_tax_rate': 'string'})
    # 2016-01-01 00:00:00
    dataFrameCSV['trans_date'] = pd.to_datetime(dataFrameCSV['trans_date'], format=('%Y-%m-%d %H:%M:%S'))
    dataFrameCSV['trans_date'] = dataFrameCSV['trans_date'].dt.strftime('%Y-%m-%d')
    dataFrameCSV['trans_gross'] = dataFrameCSV['trans_gross'].astype(float)
    dataFrameCSV['trans_tax'] = dataFrameCSV['trans_tax'].astype(float)
    dataFrameCSV['trans_net'] = dataFrameCSV['trans_net'].astype(float)


    # print(dataFrameCSV.columns)
    # print(dataFrameCSV.index)
    # print(dataFrameCSV.dtypes)

    # Create an engine instance
    alchemyEngine = create_engine('postgresql+psycopg2://xero_user:nCircle007@localhost:5432/xero', pool_recycle=5432)
    # Connect to PostgreSQL server
    # print("3.5")
    dbConnection = alchemyEngine.connect()
    # print("4")
    dbConnection.autocommit = True

    # Create a list of tuples from the dataframe values
    tuples = [tuple(x) for x in dataFrameCSV.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(dataFrameCSV.columns))
   # print("COLS", cols)
   # print("TUPLES", tuples)
   # for rr in tuples:
       # query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % ('test_transaction_detailed', cols)
    #    print(",", rr)
    #query = "INSERT INTO %s(%s) VALUES ('200', 'Sales', '2016-01-01', 'INV', 'Unit A - Rent Unit A', 'INV-0001', 13000.0, 0.0, 13000.0, 0, 'Tax on Sales') " % ('test_transaction_detailed', cols)
    # SQL quert to execute
    #query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % ('test_transaction_detailed', cols)

    #cur = dbConnection.cursor()

    dataFramePG = pd.read_sql_table('transaction_detailed', dbConnection)
    dataFramePG = dataFramePG.drop(columns=dataFramePG.columns[11])
    dataFramePG.columns = [
        "acct_code",
        "acct_name",
        "trans_date",
        "trans_type",
        "trans_des",
        "trans_ref",
        "trans_gross",
        "trans_tax",
        "trans_net",
        "trans_tax_rate",
        "trans_tax_name",
    ]

    dataFramePG.head()

    dataFramePG['trans_date'] = pd.to_datetime(dataFramePG['trans_date'], format=('%Y-%m-%d %H:%M:%S'))
    dataFramePG['trans_date'] = dataFramePG['trans_date'].dt.strftime('%Y-%m-%d')


    #dataFrameCSV['trans_tax_rate'] = '0.0%'
    # dataFrameCSV.loc[dataFrameCSV["trans_tax_rate"] == "0", "trans_tax_rate"] = "0.0%"
    # dataFrameCSV.loc[dataFrameCSV['trans_ref'] == '', 'trans_ref'] = 'None'


    dataFrameCSV['trans_tax_rate'].mask(dataFrameCSV['trans_tax_rate'] == 0, '0.00%', inplace=True)

    dataFrameCSV = dataFrameCSV.replace(numpy.np.nan, None)


    #dataFrameCSV['trans_ref'].mask(dataFrameCSV['trans_ref'] == dataFrameCSV['trans_ref'].isnull(), 'None', inplace=True)
    # dataFramePG['trans_gross'] = dataFramePG['trans_gross'].astype(float)
    # dataFramePG['trans_tax'] = dataFramePG['trans_tax'].astype(float)
    # dataFramePG['trans_net'] = dataFramePG['trans_net'].astype(float)

    print("######################################")
    print(dataFrameCSV)
    print("######################################")
    print(dataFramePG)
    print("######################################")

    # try:
    #     cur.executemany(query, tuples)
    #     dbConnection.commit()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print("Error: %s" % error)
    #     dbConnection.rollback()
    #     cur.close()
    #     return 1
    # print("execute_many() done")
    # cur.close()

    #dataFrameCSV['trans_tax_rate'] = dataFrameCSV['trans_tax_rate'].astype(str)
    # sortedCSV = dataFrameCSV.sort_values(by=['acct_code'])
    # sortedPG = dataFramePG.sort_values(by=['acct_code'])

    dataFrameCSV.reset_index(drop=True, inplace=True)
    dataFramePG.reset_index(drop=True, inplace=True)

    # print(dataFrameCSV.reset_index(drop=True).equals(dataFramePG.reset_index(drop=True)))
    # print(dataFrameCSV.reset_index(drop=True) == (dataFramePG.reset_index(drop=True)))

    #print(dataFrameCSV.iloc[3011], dataFramePG.iloc[3011])
    # print(dataFrameCSV.equals(dataFramePG))
    # print("-------------------------------------")
    # unchanged_rows = dataFrameCSV.merge(dataFramePG, how='inner', indicator=False)
    # print("unchanged or same rows ")
    # print(unchanged_rows.to_string())

    # print("-------------------------------------")
    # changed_rows = pd.concat([dataFrameCSV, dataFramePG]).drop_duplicates(keep=False)
    # print("changed rows")
    # print(changed_rows.to_string())
    # print("-------------------------------------")
   # print(dataFrameCSV.iloc[324], dataFramePG.iloc[324])

    #write dataframe to table
    dataFrameCSV.to_sql('test_transaction_detailed3', con=dbConnection, if_exists='replace', index=False)
    #dataFrameCSV.to_sql('test_transaction_detailed3', con=dbConnection, if_exists='append', index=False)
    # compare the two PG tables
    queryCompare = """ select  acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name 
from transaction_detailed 
where not exists (select  acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name 
from test_transaction_detailed3);  """
    dataFramePGTTD3 = pd.read_sql(queryCompare, dbConnection)

    print(len(dataFramePGTTD3))
    if len(dataFramePGTTD3.columns) >= 0:
        print("Compare is empty. Nothing to do", dataFramePGTTD3)
    else:
        print("Compare is not empty. Lets add rows to table", dataFramePGTTD3)



    # Read data from PostgreSQL database table and load into a DataFrame instance
    #dataFrame = pd.read_sql("select * from \"transaction_detailed\"", dbConnection)

    #show(dataFrameCSV)

    # check = dataFrameCSV.compare(dataFramePG)
    # print("..",check)

    sys.exit(85)
    # Using psql
    # conn = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
    # cur = conn.cursor()
    # cur.execute("select * from transaction_detailed")


    #dataPG = cur.fetchall()
    #print(type(dataPG), len(dataPG))
    #print(dataPG)
    # for row_csv in CSVl:
    #     if row_csv[5] == "":
    #         row_csv[5] = 'None'
    #     #
    #     #         print(". l", rowl)
    #     #print(type(row_csv), len(row_csv), row_csv)
    #
    #     #for r in dataPG:
    #         #print(type(r), r)
    #         # if r[11]:
    #         #     del r[11]
    #     #print(type(r), len(r), r)
    #
    #     if row_csv == r :
    #         print("y ", row_csv)
    #         print("y", r)
    #     else:
    #         print("n ", row_csv)
    #         print("n", r)
    # Create an engine instance
    #alchemyEngine = create_engine('postgresql+psycopg2://xero_user:nCircle007@localhost:5432/xero', pool_recycle=5432)
    # Connect to PostgreSQL server
    #dbConnection = alchemyEngine.connect()
    # Read data from PostgreSQL database table and load into a DataFrame instance
    #dataFrame = pd.read_sql("select * from \"transaction_detailed\"", dbConnection)

    # pd.set_option('display.expand_frame_repr', False)
    #print(dataFrame)

    # dataFrame.columns = [
    #     "acct_code",
    #     "acct_name",
    #     "trans_date",
    #     "trans_type",
    #     "trans_des",
    #     "trans_ref",
    #     "trans_gross",
    #     "trans_tax",
    #     "trans_net",
    #     "trans_tax_rate",
    #     "trans_tax_name",
    #     "record_id",
    # ]
    # dataFrame.head()




    #print(dataFrameCSV.columns)
    #show(dataFrameCSV)

    #dataFrameNew = dataFrame.drop(columns=dataFrame.columns[11])

    # dataFrameNew.columns = [
    #     "acct_code",
    #     "acct_name",
    #     "trans_date",
    #     "trans_type",
    #     "trans_des",
    #     "trans_ref",
    #     "trans_gross",
    #     "trans_tax",
    #     "trans_net",
    #     "trans_tax_rate",
    #     "trans_tax_name",
    # ]
    # dataFrameNew.head()
    # dataFrameNew = dataFrameNew.astype(str)
        #{'trans_gross': 'float', 'trans_tax': 'float', 'trans_net': 'float', 'trans_tax_rate': 'str'})



    #print(dataFrameCSV)
    # print(dataFrameNew.columns)
    # print(dataFrameNew.index)
    # print(dataFrameNew.dtypes)

    #print(dataFrameNew)

    #dataFrameCSV = dataFrameCSV.astype({'trans_gross':'float','trans_tax':'float','trans_net':'float','trans_tax_rate':'str'})
    #dataFrameNew = dataFrameNew.astype({'trans_gross':'float','trans_tax':'float','trans_net':'float','trans_tax_rate':'str'})

    #dataFrameCSV = dataFrameCSV.astype(str)
    #dataFrameNew - dataFrameNew.astype(str)

    # dfCSV = dataFrameCSV.values.tolist()
    #dfNew = dataFrameNew.values.tolist()
    # print(".. ..",dfNew)
    # print()
    # print("..\..",CSVfh)

# .     ['200', 'Sales', '2016-01-01', 'INV', 'Unit A - Dues Unit A', 'INV-0001', '1000.0', '0', '1000.0', '0.00%', 'Tax on Sales']
# ..    ['200', 'Sales', '2016-01-01', 'INV', 'Unit A - Dues Unit A', 'INV-0001', '1000.0', '0.0', '1000.0', '0.00%', 'Tax on Sales']

# .  ['200', 'Sales', '2016-01-01', 'INV', 'Unit A - Dues Unit A', 'INV-0001', '1000.0', '0.0', '1000.0', '0.00%', 'Tax on Sales']
# .. ['200', 'Sales', '2016-01-01', 'INV', 'Unit A - Dues Unit A', 'INV-0001', '1000.0', '0.0', '1000.0', '0.00%', 'Tax on Sales']

# .    830,   Income Tax Payable,  2016-08-14,    EC,   Jasmin D - Bir monthly tax,,          -2040,0.0,-2040,0.00%,Tax Exempt
# .. ['830', 'Income Tax Payable', '2016-08-14', 'EC', 'Jasmin D - Bir monthly tax', 'None', '-2040.0', '0.0', '-2040.0', '0.00%', 'Tax Exempt']
#     for row_csv in CSVfh:
#         rowl = row_csv.split(",")
#         print(". ", type(rowl), rowl)
#         if rowl[5] == "":
#             rowl[5] = 'None'
#
#         print(". l", rowl)
#
#




     #   if row_csv not in dfNew:
     #       print('not found it ', row_csv)

      #  else:
       #     print('found it ', row_csv)
    #dataFrameCSV.sort_index().sort_values(axis=1) == dataFrameNew.sort_index().sort_values(axis=1)
    # print(".",dataFrameNew.equals(dataFrameCSV))
    # check = dataFrameCSV.compare(dataFrameNew)
    # print("..",check)

    #set_dfCSV = set(dfCSV)
    #set_dfNew = set(dfNew)
    # if set_dfCSV == set_dfNew:
    #     print("Lists are equal")
    # else:
    #     print("Lists  are not equal")


#    print(dataFrameNew.compare(dataFrameCSV))


    #show(dataFrame)
    # Close the database connection
    dbConnection.close()
    conn.close()

if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
