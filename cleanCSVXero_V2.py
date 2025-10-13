import sys
from datetime import datetime
import pandas as pd

def cleanXeroCSVfile(xls_file):

    # Account Code	Account	Date	Account Type	Contact	Description	Invoice Number	Reference	Gross	Tax	Source
    # Related Account	Net	Tax Rate	Contact Group	Debit	Credit	Tax Rate NameAccount Code	Account	Date
    # Account Type	Contact	Description	Invoice Number	Reference	Gross	Tax	Source	Related Account	Net	Tax Rate
    # Contact Group	Debit	Credit	Tax Rate Name

    CSVlClean=[]


    # Read your Excel file
    df = pd.read_excel(xls_file, skiprows=5)

    # Show column names to verify exact match
    print("Column names:", df.columns.tolist())

    # Strip column names of extra spaces
    df.columns = df.columns.str.strip()

    # Safely convert Account Code to string, strip spaces, then back to int if possible
    # df['Account Code'] = pd.to_numeric(df['Account Code'], errors='coerce')

    # Drop rows with Account Code == 801
    # df = df[df['Account Code'] != 801]

    # Exclude rows where first column == '801' (string)
    #df = df[df.iloc[:, 0] != '801']

    # Define values to exclude
    exclude_values = ['801', '490', '610', '713', '749', '800', '830', '840', '960', 'Total', None, '']

    # Filter out rows where first column matches any exclude value
    #df = df[~df.iloc[:, 0].isin(exclude_values)]

    # Keep rows NOT in exclude_values and NOT null
    df = df[~df.iloc[:, 0].isin(exclude_values) & df.iloc[:, 0].notna()]


    # Iterate through only the first 10 rows
    # for index, row in df.head(10).iterrows():
    #    print(row)
    #    print("-----")

    # Iterate and print each row in a single line (first 10 rows only)
    # for index, row in df.head(10).iterrows():
    # print(', '.join([f"{col}: {row[col]}" for col in df.columns]))

    # Print just the values of the first 10 rows, one row per line
    try:
        for index, row in df.iterrows():
            #print(*row.values, sep=', ')
            #if row.values[0] in ('801', '830', '840', '960', '490', '610', '713', '749', '800'):
            #    print("IGNORE ", row.values)
            #else:
            #    print("VALID", row.values)

            # if str(row.values[0]) != "nan" or str(row.values[0]) != "NaT" :
            #    print(len(str(row.values[0])))
            print(row.values[0], row.values[1], row.values[2], row.values[3],
                                               row.values[4], row.values[5],
                                               row.values[6], row.values[7], row.values[8], row.values[9],
                                               row.values[10], row.values[11],
                                               row.values[12], row.values[13], row.values[14], row.values[15],
                                               row.values[16], row.values[17]
                  ,sep=', ')
            # else :
            #     print("..", row.values[0])

        #for row in CSVl:
            #print("unclean csv", len(row), row)
            #if len(row) > 0 and len(row[0]) > 0 and (row[0] is not None
                # and row[0] != '\ufeff'
                # and 'Account Transactions' not in row[0]
                # and 'Patinio' not in row[0]
                # and 'For the period' not in row[0]
                # and 'Account Code' not in row[0]
                # and 'Accrual Basis' not in row[0]
                # and 'Total' not in row[0]
                # and '490' not in row[0]
                # and '610' not in row[0]
                # and '713' not in row[0]
                # and '749' not in row[0]
                # and '800' not in row[0]
                # and '801' not in row[0]
                # and '830' not in row[0]
                # and '840' not in row[0]
                # and '960' not in row[0]):
                #
                # #print("..", row)
                #
                # row[0] = row[0].replace('\ufeff', '')
                # row[4] = row[4].replace("\\", "").replace('"', '').replace("\n", "").replace("\r", "")
                # row[2] = datetime.strptime(row[2], '%d/%m/%Y')
                # row[2] = datetime.strftime(row[2], '%Y-%m-%d')
                # row[6] = row[6].replace("₱", "")
                # row[6] = row[6].replace(",", "")
                # row[6] = float(row[6])
                # row[7] = row[7].replace("₱", "")
                # row[7] = row[7].replace(",", "")
                # row[7] = float(row[7])
                # row[8] = row[8].replace("₱", "")
                # row[8] = row[8].replace(",", "")
                # row[12] = row[12].replace(",", "")
                # row[15] = row[15].replace(",", "")
                # row[16] = row[16].replace(",", "")
                # row[8] = float(row[8])
                #if row[14] == '0.0%':
                #     row[14] = '0.00%'

                #if row[0] == '445':
                #print("Cleaning xero row..>>", row)
                #print(">>", row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17])
            Cclean=[row.values[0], row.values[1], row.values[2], row.values[3],
                                               row.values[4], row.values[5],
                                               row.values[6], row.values[7], row.values[8], row.values[9],
                                               row.values[10], row.values[11],
                                               row.values[12], row.values[13], row.values[14], row.values[15],
                                               row.values[16], row.values[17] ]

                        #row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]]
            CSVlClean.append(Cclean)

        # for ee in CSVlClean:
        #     print("clean CSV ",ee)
        # exit(99)
        return(CSVlClean)

    except Exception as mie:
        print("Error 8: The Xero file could not be processed and clean:", mie)
        sys.exit(8)
