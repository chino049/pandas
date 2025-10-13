

#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasgui
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pywin32
#  C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install xlrd
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install pandasql
# C:\Users\jesus.ordonez\AppData\Local\Programs\Python\Python310\Scripts\pip3 install openpyxl

import csv
import sys
from datetime import datetime
import psycopg2


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
            #print("unclean csv", row)
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

        # for oo in pglClean:
        #     print("clean pg", oo)

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

    print("\nDone with integration,now lets check for duplicate records")
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
        print("ERROR: Cannot reach/read the database or table", pp)

    cur2.close()
    conn2.close()



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


