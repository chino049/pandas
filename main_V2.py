import csv
import sys
from datetime import datetime
from psycopg2.sql import Identifier, SQL
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import plotly
import plotly.graph_objs as go
import plotly.express as px

#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasgui
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pywin32
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install xlrd
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasql
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install openpyxl
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import openpyxl
#import pandas as pd
import pandas.io.sql as psql
import pandasql as ps

from IPython.core.display_functions import display
#from pandas.compat import numpy
from pandas.io.formats import string

from pandasgui import show

import psycopg2
#from sqlalchemy import create_engine
import xlrd

#import pywin32
import win32api
def graphs():
    # plt.set_ylabel('Y LABEL')
    # plt.set_xlabel('X LABEL')
    # plt.set_title('TITLE_HERE')
    try:
        # Using psql
        conn = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, \
        trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name \
        FROM transaction_detailed \
        WHERE (trans_date >= timestamp with time zone '2022-01-01 00:00:00.000-08:00' \
        AND trans_date < timestamp with time zone '2023-01-01 00:00:00.000-08:00' \
        AND (trans_ref <> 'transpo' \
        OR trans_ref IS NULL) \
    	AND (trans_ref <> 'Transpo' \
    	OR trans_ref IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo ' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo allowance' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo allowance of bernadeth ' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transpo allowance payment property tax' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo allowance quarterly' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo allowance to notarial of new contract' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo allowance/3rd quarter' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo bernadeth' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transpo Bernadeth for filing (ITR,BIR quarterLy)' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo filing property tax &montly tax' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transpo filing tax' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo filing taxes'\
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo filing taxes ' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo for bringing the A/C' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo for filing at cthall' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transpo for filing taxes'\
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo for notarial' \
    	OR trans_des IS NULL)\
    	AND (trans_des <> 'Jasmin D - transpo for notarial ' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo going to cthall for reporting to treasurer office regarding tax mapping.then going to bldg for some issues to brgy.' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo notarial' \
    	OR trans_des IS NULL)\
    	AND (trans_des <> 'Jasmin D - transpo of materials'\
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo to purchase a/c' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transpo to talk to new tenant and signing of contract' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transpo/4quarter' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - Transportation' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - transportation/to purchased garbage tub and pots' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'lights - transpo' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Transpo - Transpo filing Tax' \
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - gas'\
    	OR trans_des IS NULL) \
    	AND (trans_des <> 'Jasmin D - refill gas tank' \
    	OR trans_des IS NULL) \
    	AND (acct_name = 'Payment to Owners' \
    	OR acct_name = 'Tranportation allowance, Travel - National' \
    	OR acct_name = 'Christmas Gifts')) order by trans_date ")


        xx=[]
        yy=[]
        pgl = cur.fetchall()
        #print(type(pgl), pgl)
        for rrr in pgl:
            #print(".", rrr)
            xx.append(rrr[4])
            yy.append(rrr[6])
            #print(rrr)
        # print(xx)
        # print(yy)

    except Exception as pp:
        print("ERROR: Cannot reach/read the database or table", pp)

    cur.close()
    conn.close()

    try:
        # Using psql
        conn1 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur1 = conn1.cursor()
        cur1.execute("SELECT  acct_code, acct_name, trans_type, trans_date, trans_des, trans_ref, \
         trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name FROM transaction_detailed \
         WHERE(trans_date >= timestamp with time zone '2022-01-01' AND trans_date < timestamp with time zone '2023-01-01' \
         AND (acct_code = '473' OR acct_code = '476' OR acct_code = '429' OR acct_code = '420' OR acct_code = '408'  \
                OR acct_code = '461' OR acct_code = '441' OR acct_code = '475')) order by trans_date")

        xx1 = []
        yy1 = []
        pgl1 = cur1.fetchall()
        #print(type(pgl1), pgl1)
        for rr in pgl1:
           # print(".", rrr)
            xx1.append(rr[4])
            yy1.append(rr[6])
            # print(rrr)
        # print(xx1)
        # print(yy1)

    except Exception as ppd:
        print("ERROR: Cannot reach/read the database or table", ppd)

    cur1.close()
    conn1.close()


    # trace0 = go.Bar( #x,y)
    #     #x=[1, 2, 3, 4],
    #     x=xx,
    #     #y=[10, 15, 13, 17]
    #     y=yy
    # )
    # trace0 = go.Scatter( #x,y)
    #     #x=[1, 2, 3, 4],
    #     x=xx,
    #     #y=[10, 15, 13, 17]
    #     y=yy
    # )
    # trace1 = go.Scatter(
    #     x=[1, 2, 3, 4],
    #     y=[16, 5, 11, 9]
    # )
    #data = go.Data([trace0]) #, trace1])
    #data1 = go.Data([trace0])
    #
    #plotly.offline.iplot(data) #, filename = 'basic-line')

    # fig = go.Figure(
    #     #data=[go.Bar(y=[2, 1, 3])],
    #     data=[go.Bar(trace0)],
    #     layout_title_text="A Figure Displaying Itself"
    # )
    #fig = px.bar(long_df, x="nation", y="count", color="medal", title="Long-Form Input")
    #fig = px.bar(pgl, x='trans_des', y='trans_gross')
    #fig = px.bar(trace0,  title="Long-Form Input")
    fig = px.bar(x = yy, y = xx, color_discrete_sequence =['blue'])    #
    fig.update_layout(width=1300, height=500, bargap=0.05)


    # def SetColor(y):
    #     if (y >= 100):
    #         return "red"
    #     elif (y >= 50):
    #         return "yellow"
    #     elif (y >= 0):
    #         return "green"

    #fig.update_layout(xaxis=dict(tickformat="%Y-%m-%d"))
    #fig.update_xaxes(tickformat="%Y-%m-%d")
    #print(fig.data)
    fig.show()

    fig1 = px.bar(x=yy1, y=xx1, color_discrete_sequence =['green'])
    fig1.update_layout(width=1300, height=2000, bargap=0.05)

    fig1.show()

    #plotly.offline.iplot(data1, filename='basic-pie')

    try:
        # Using psql
        conn2 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur2 = conn2.cursor()
        cur2.execute("SELECT acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, \
            trans_tax, trans_net, trans_tax_rate, trans_tax_name FROM transaction_detailed \
            WHERE (trans_date >= '2022-01-01' AND trans_date < '2023-01-01') \
            AND (trans_des = 'Sal Admin - salary Admin' \
            OR trans_des = 'Jasmin D - admin' OR trans_des = 'Jasmin D - admin sal' \
            OR trans_des = 'Jasmin D - Admin sal' OR trans_des = 'Jasmin D - admin sal.' \
            OR trans_des = 'Jasmin D - admin salary' OR trans_des = 'Jasmin D - AdminSal' \
            OR trans_des = 'Jasmin D - sal admin' OR trans_des = 'Jasmin D - Sal admin' \
            OR trans_des = 'Jasmin D - Sal Admin' OR trans_des = 'Jasmin D - sal.admin' \
            OR trans_des = 'Jasmin D - sal.Admin' OR trans_des = 'Jasmin D - Sal.admin' \
            OR trans_des = 'Jasmin D - salary admin' OR trans_des = 'Jasmin D - salary Admin' \
            OR trans_des = 'Jasmin D - Salary admin' OR trans_des = 'Jasmin D - Salary Admin' \
            OR trans_des = 'Jasmin D - salary administrator' OR trans_des = 'sal - sal.admin' \
            OR trans_des = 'sal - salary admin' OR trans_des = 'Sal Admin - salary' \
            OR trans_des = 'Sal Admin - salary admin' OR trans_des = 'wages salary - salary admin' \
            OR trans_des = 'Jasmin D -  sal.caretaker') order by trans_date")

        xx2 = []
        yy2 = []
        pgl2 = cur2.fetchall()
        print(type(pgl2), pgl2)
        for rr in pgl2:
           # print(".", rrr)
            xx2.append(rr[6])
            yy2.append(rr[2])
            # print(rrr)
        print(xx2)
        print(yy2)

        conn22 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur22 = conn22.cursor()
        cur22.execute("SELECT acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, \
                trans_tax, trans_net, trans_tax_rate, trans_tax_name FROM transaction_detailed \
                WHERE (trans_date >= '2022-01-01' AND trans_date < '2023-01-01') \
                AND (trans_des = 'Jasmin D -  sal.caretaker' OR trans_des = 'Jasmin D - salary Mike' OR trans_des = 'Jasmin D - salary mike' OR trans_des = 'Jasmin D - Salary  Mike' OR trans_des = 'Jasmin D - sal.Mike' OR trans_des = 'Jasmin D - sal.mike' OR trans_des = 'sal caretaker - salary mike' OR trans_des = 'sal caretaker - salary Mike' OR trans_des = 'Jasmin D - care taker' OR trans_des = 'Jasmin D - caretaker' OR trans_des = 'Jasmin D - caretaker sal.' OR trans_des = 'Jasmin D - sal caretaker' OR trans_des = 'Jasmin D - Sal caretaker' OR trans_des = 'Jasmin D - Sal Caretaker' OR trans_des = 'Jasmin D - sal.caretaker' OR trans_des = 'Jasmin D - sal.Caretaker' OR trans_des = 'Jasmin D - salary care taker' OR trans_des = 'Jasmin D - salary caretaker' OR trans_des = 'Jasmin D - Salary Caretaker' OR trans_des = 'Jasmin D - salary of caretaker' OR trans_des = 'sal - sal.caretaker' OR trans_des = 'sal caretaker - salary caretaker' OR trans_des = 'Sal of Michael - salary caretaker' OR trans_des = 'Jasmin D - michael' OR trans_des = 'Jasmin D - Michael' OR trans_des = 'Jasmin D - Michael sal' OR trans_des = 'Jasmin D - Michael sal.' OR trans_des = 'Jasmin D - salary michael' OR trans_des = 'Jasmin D - salary Michael' OR trans_des = 'Jasmin D - salary of Michael' OR trans_des = 'Jasmin D - Salary of Michael' OR trans_des = 'Jasmin D - sal Michael' OR trans_des = 'Jasmin D - sal.michael' OR trans_des = 'Jasmin D - Sal.Michael' OR trans_des = 'Jasmin D - sal.Michael') order by trans_date")

        xx22 = []
        yy22 = []
        pgl22 = cur22.fetchall()
        print(type(pgl22), pgl22)
        for rr in pgl22:
            # print(".", rrr)
            xx22.append(rr[6])
            yy22.append(rr[2])
            # print(rrr)
        print(xx22)
        print(yy22)


    except Exception as ppdd:
        print("ERROR: Cannot reach/read the database or table", ppdd)

    cur2.close()
    conn2.close()
    cur22.close()
    conn22.close()
    #sys.exit(99)
    fig2 = px.line(x=yy2, y=xx2, color_discrete_sequence =['red'])
    #fig2.update_layout(x=yy22, y=xx22, color_discrete_sequence=['blue'])
    #fig2.update_layout(width=1300, height=2000, bargap=0.05)
    fig2.update_traces(mode='markers+lines')

    fig2.show()
    trace0 = go.Scatter(  # x,y)
            #x=[1, 2, 3, 4],
            x=xx2,
            #y=[10, 15, 13, 17]
            y=yy2
        )
    trace1 = go.Scatter(  # x,y)
        # x=[1, 2, 3, 4],
        x=xx22,
        # y=[10, 15, 13, 17]
        y=yy22
    )
    data = go.Data([trace0] , [trace1])
    plotly.offline.iplot(data)
def run(csv_file, dry_run):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Begin database integration')

    try:
        with open(csv_file, "r",
              encoding='utf-8') as file:
            CSVfh = csv.reader(file)
            CSVl = list(CSVfh)
    except Exception as fe:
        print("ERROR: Reading or retrieving the CSV file", fe)

    #print(len(CSVl), type(CSVl))
    CSVlClean=[]
    try:
        for row in CSVl:
            print("unclean csv", row)
            if len(row[0]) > 0:
                row[0] = row[0].replace('\ufeff', '')
                row[4] = row[4].replace("\\", "").replace('"', '').replace("\n", "").replace("\r", "")
                #row[4] = row[4].strip("\\'\"")
                #print("re 4", re[4])
                row[2] = datetime.strptime(row[2], '%d/%m/%Y')
                row[2] = datetime.strftime(row[2], '%Y-%m-%d')
                row[6] = row[6].replace("₱", "")
                row[6] = row[6].replace(",", "")
                row[6] = float(row[6])
                # if row[6].is_integer():
                #     row[6] = round(row[6], 1)

                row[7] = row[7].replace("₱", "")
                row[7] = row[7].replace(",", "")
                row[7] = float(row[7])
                # if row[7].is_integer():
                #     row[7] = round(row[7], 1)

                row[8] = row[8].replace("₱", "")
                row[8] = row[8].replace(",", "")
                row[8] = float(row[8])
                if row[9] == '0.0%':
                    row[9] = '0.00%'
                # if row[8].is_integer():
                #     row[8] = round(row[8], 1)
                #print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
                Cclean=[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]
                CSVlClean.append(Cclean)

        # for ee in CSVlClean:
        #     print("clean CSV ",ee)

    except Exception as ie:
        print("Error 8", ie)
        pass

    try:
        #Using psql
        conn = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("select * from transaction_detailed")
        pgl = cur.fetchall()
        #print(type(pgl), pgl)

    except Exception as pp:
        print("ERROR: Cannot reach/read the database or table")

    cur.close()
    conn.close()

    # print("length CSV", len(CSVlClean))
    # print("length pgl", len(pgl))
    try:
        pglClean=[]
        for re in pgl:
            re=list(re)
            #print(re)
            re[0] = re[0].replace('\ufeff', '')
            re[2] = str(re[2]) #.str(datetime.datetime('%Y-%m-%d'))
            re[4] = re[4].replace("\r", "").replace("\n", "")
            if re[5] == None:
                re[5] = ""


            pclean=[re[0], re[1], re[2], re[3], re[4], re[5], re[6], re[7], re[8], re[9], re[10]]
            #print("..", pclean)
            pglClean.append(pclean)

        for oo in pglClean:
            print("clean pg", oo)

    except Exception as sw:
        print("error 23", sw)

    try:
        # CSVlClean.sort()
        # pglClean.sort()
        #print("dryrun", dry_run)
        # Using psql
        if not dry_run:
            conn1 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
            cur1 = conn1.cursor()

        for li in CSVlClean:
            print(".",end=".")
            if li not in pglClean:
                if dry_run:
                    print("Dryrun - will not integrate")

                print("Missing entries on database transaction_detailed: ")
                print(li)

                if not dry_run:
                    try:
                        postgres_insert_query = """ INSERT INTO transaction_detailed (acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        record_to_insert = li[0], li[1], li[2], li[3], li[4], li[5], li[6], li[7], li[8], li[9], li[10]
                        # print(".",  postgres_insert_query)
                        # print("..", record_to_insert)
                        cur1.execute(postgres_insert_query, record_to_insert)
                        conn1.commit() # <- We MUST commit to reflect the inserted data

                    except Exception as ddb:
                        print("Error inserting into table", ddb)
        if not dry_run:
            cur1.close()
            conn1.close()

    except Exception as rwe:
        print("Error 62", rwe)

    print("Done inserting now lets check for duplicate records")
    try:
        #Using psql
        conn2 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
        cur2 = conn2.cursor()
        cur2.execute("select acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, \
            trans_tax, trans_net, trans_tax_rate, trans_tax_name, COUNT(*) AS Count from transaction_detailed \
            group by acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, \
            trans_net, trans_tax_rate, trans_tax_name HAVING COUNT(*) > 1")
        dup = cur2.fetchall()
        print("Duplicate records: ", dup)

    except Exception as pp:
        print("ERROR: Cannot reach/read the database or table")

    cur.close()
    conn.close()



if __name__ == '__main__':
    # print(len(sys.argv))
    # print(sys.argv[0])
    # print(sys.argv[1])

    dryrun = False
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            print("For dryrun ensure the second argument is called dryrun", sys.argv[2])
            dryrun=True
        run(sys.argv[1], dryrun)
    else:
        print("Please enter the name of the CSV file to integrate with the database")

    #graphs()
