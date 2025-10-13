

# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasgui
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pywin32
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install xlrd
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasql
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install openpyxl

import csv
import os
import sys

import pandas as pd
from datetime import datetime, date
from tokenize import String

import psycopg2
from cleanCSVfidelity import cleanFidelityCSVfile as cff
from cleanCSVXero_V2 import cleanXeroCSVfile as cxf
from PGxeroConnect import pgConn
from readFidelity import readPositions



xeroDB = 'bank_transactions'
#xeroDB = 'test_transaction_detailed'

def run(app, xls_file, dry_run):
    print(f'Begin database integration')

    if app == 'xero':
        print("App Xero")
        CSVxClean = cxf(xls_file)

        #print("CSVxClean", CSVxClean)
        db = 'xero'
        db_user = 'xero_user'
        db_pw = 'nCircle007'
        #db_host = '10.0.0.70'

        #db_host = '10.0.0.177'
        db_host = 'localhost'
        db_port = '5432'

        (cur,conn) = pgConn(db, db_user, db_pw, db_host, db_port)

        dt = str(datetime.now().strftime("%Y_%m_%d"))
        print(dt)
       # exit(999)

        try:
            # CSVlClean.sort()
            # pglClean.sort()
            #print("dryrun", dry_run)
            # Using psql
            if not dry_run:
                (cur1, conn1) = pgConn(db, db_user, db_pw, db_host, db_port)
                # conn1 = psycopg2.connect(database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
                # cur1 = conn1.cursor()
                cur1.execute("CREATE TABLE bank_transactions_"+dt+" AS SELECT * FROM bank_transactions;")
                conn1.commit()
                cur1.execute("""truncate table bank_transactions;""")
                conn1.commit()


            for li in CSVxClean:
                print("Clean CSV ....................", li)
              #  print("............................pglclean", pglClean )
              #  if li not in pglClean:
                if dry_run:
                    print("Dryrun - will not integrate")

                    #print("Missing entries on database bank_transactions: ")
                    print(li)

# create table bank_transactions as select acct_code, acct_name, trans_date, acct_type, contact, trans_des, invoice, trans_ref, gross, tax, source, related_account, trans_net, tax_rate, contact_group, trans_debit, trans_credit, trans_rate_name FROM old;
# CREATE table bank_transactions_102124 as table bank_transactions;

                elif not dry_run:
                    try:
                        postgres_insert_query = """ INSERT INTO """+xeroDB+""" (acct_code, acct_name, trans_date, acct_type, contact, trans_des, invoice, trans_ref, gross, tax, source, related_account, trans_net, tax_rate, contact_group, trans_debit, trans_credit, trans_rate_name) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        # test
                        #postgres_insert_query = """ INSERT INTO test_transaction_detailed (acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, trans_net, trans_tax_rate, trans_tax_name) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                        record_to_insert = li[0], li[1], li[2], li[3], li[4], li[5], li[6], li[7], li[8], li[9], li[10], li[11], li[12], li[13], li[14], li[15], li[16], li[17]
                        # print(".",  postgres_insert_query)
                        print("Inserting record... ", record_to_insert)
                        cur1.execute(postgres_insert_query, record_to_insert)
                        conn1.commit() # <- We MUST commit to reflect the inserted data

                    except Exception as ddb:

                        print("Error 38 inserting into bank_transactions", ddb)
                        sys.exit(38)
            if not dry_run:
                print("Renaming file ", xls_file, "to ", xls_file+"processed")
                os.rename(xls_file, xls_file+"processed")

                cur1.close()
                conn1.close()

        except Exception as rwe:
            print("Error 62", rwe)

        print("\nDone with integration,now lets check for duplicate records")

        try:
            #Using psql

            (cur2, conn2) = pgConn(db, db_user, db_pw, db_host, db_port)

            cur2.execute("select acct_code, acct_name, trans_date, acct_type, contact, trans_des, invoice, trans_ref, gross, \
            tax, source, related_account, trans_net, tax_rate, contact_group, trans_debit, trans_credit, \
            trans_rate_name , COUNT(*) AS Count from "+xeroDB+"  \
            group by acct_code, acct_name, trans_date, acct_type, contact, trans_des, invoice, trans_ref, gross, \
            tax, source, related_account, trans_net, tax_rate, contact_group, trans_debit, trans_credit, \
            trans_rate_name HAVING COUNT(*) > 1")

            # test
            # cur2.execute("select acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, \
            #                 trans_tax, trans_net, trans_tax_rate, trans_tax_name, COUNT(*) AS Count from test_transaction_detailed \
            #                 group by acct_code, acct_name, trans_date, trans_type, trans_des, trans_ref, trans_gross, trans_tax, \
            #                 trans_net, trans_tax_rate, trans_tax_name HAVING COUNT(*) > 1")
            dup = cur2.fetchall()
            print("Duplicate records: ", dup)

        except Exception as pp:
            print("ERROR: Cannot reach/read the database or table", pp)

        cur2.close()
        conn2.close()

    elif app == 'fidelity':
        print("App Fidelity")

        CSVfClean = cff(xls_file)
        # change that to fidliety csv?

        db = 'fidelity'
        db_user = 'xero_user'
        db_pw = 'nCircle007'
        #db_host = '192.168.1.108'
        db_host = 'localhost'
        db_port = '5432'

        if not dry_run:
            (cur1, conn1) = pgConn(db, db_user, db_pw, db_host, db_port)
            # postgres_truncate_query = """ truncate positions"""
            # cur1.execute(postgres_truncate_query)


        for li in CSVfClean:
            print(".", end=".")
            #if li not in pglClean:
            if dry_run:
                print("Dryrun - will not integrate")

            #print("Missing entries on database transaction_detailed: ")
            print("Trying to insert:", li)

            if not dry_run:
                try:

                    # postgres_insert_query = """INSERT INTO positions (acct, name, symbol, des, quantity, last_price,
                    # last_price_change, current_value, today_gain_money, today_gain_percentage, total_gain_money,
                    # total_gain_percentage, acct_percentage, total_cost_basis, avg_cost_basis, acct_type)
                    #  values ('Z21480840', 'Trust: Under Agreement', 'BDC', 'BELDEN INC', 129.0, 76.3, 2.86, 9842.7, 368.94, 3.89, 2955.39, 42.91, 29.76, 6887.31, 53.39, 'Cash')"""

                    # test
                    if li[1] == 'Traditional IRA':
                        symbol = 'I:'+li[2]
                    elif li[1] == 'ROTH IRA':
                        symbol = 'R:'+li[2]
                    elif  li[1] == 'Trust: Under Agreement':
                        symbol = 'B:'+li[2]
                    elif li[1] == 'FORTRA 401(K) PLAN':
                        symbol = 'K:'+li[2]
                    else :
                        symbol = li[2]
                    print("JOP 745 symbol", symbol)

                    #ostgres_insert_query = """ INSERT INTO test_positions (acct, name, symbol, des, quantity, last_price,
                    postgres_insert_query = """ INSERT INTO positions (acct, name, symbol, des, quantity, last_price,
                    last_price_change, current_value, today_gain_money, today_gain_percentage, 
                    total_gain_money, total_gain_percentage, acct_percentage, 
                    total_cost_basis, avg_cost_basis, acct_type, rec_date) 
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    record_to_insert = li[0], li[1], symbol, li[3], li[4], li[5], li[6], li[7], li[8], li[9], li[10], li[11], li[12], li[13], li[14] , li[15], li[16]
                    #print("..",        li[0], li[1], li[2], li[3], li[4], li[5], li[6], li[7], li[8], li[9], li[10], li[11], li[12], li[13], li[14] ,li[15])
                    #print(type(li[0]), type(li[1]), type(li[2]), type(li[3]), type(li[4]), type(li[5]), type(li[6]), type(li[7]), type(li[8]), type(li[9]),
                          #type(li[10]), type(li[11]), type(li[12]), type(li[13]), type(li[14]), type(li[15]))
                    cur1.execute(postgres_insert_query, record_to_insert)
                    #cur1.execute(postgres_insert_query)
                    conn1.commit()  # <- We MUST commit to reflect the inserted data

                except Exception as ddb:
                    print("Error inserting into positions table", ddb)

        if not dry_run:
            print("Renaming file ", xls_file, "to ", xls_file + "processed")
            os.rename(xls_file, xls_file+"processed")

            cur1.close()
            conn1.close()

        #readFidelity = readPositions()

if __name__ == '__main__':
    # print(len(sys.argv))
    # print(sys.argv[0])
    print(sys.argv[1])
    # print(sys.argv[2])
    dryrun = False
    if len(sys.argv) > 1:
        if sys.argv[1].endswith(".csv") or sys.argv[1].endswith(".xlsx"):
            if "xero" in sys.argv[1] or "Patinio" in sys.argv[1]:
                app='xero'
            elif "fidelity" in sys.argv[1]:
                app='fidelity'
            else:
                print("Error: 15 File name must contain the application name; xero or fidelity", sys.argv[1])
                sys.exit(15)

            # add is the file does not end with .csv the fail if sys.argv[2]
            if len(sys.argv) > 2:
                if sys.argv[2] == 'dryrun':
                    print("For dryrun ensure the second argument is called dryrun", sys.argv[2])
                    dryrun=True

            run(app,sys.argv[1], dryrun)
                # elif sys.argv[2] == 'fidelity':
                #     run(sys.argv[2])
        else :
            print("Error:16 File extension is not .csv")
            sys.exit(16)
    else:
        print("Please enter the name of the CSV file to integrate with the database")

# Copy Table Structure Only (No Data)
# CREATE TABLE bank_transactions AS SELECT * FROM bank_transactions_123124 WHERE false;

# Copy Table Structure and Data
# CREATE TABLE new_table AS SELECT * FROM original_table;

# Delete All rows - faster
# truncate table table_name
