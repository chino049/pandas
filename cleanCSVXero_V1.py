import sys
from datetime import datetime

def cleanXeroCSVfile(CSVl):

# Account Code	Account	Date	Account Type	Contact	Description	Invoice Number	Reference	Gross	Tax	Source
# Related Account	Net	Tax Rate	Contact Group	Debit	Credit	Tax Rate NameAccount Code	Account	Date
# Account Type	Contact	Description	Invoice Number	Reference	Gross	Tax	Source	Related Account	Net	Tax Rate
# Contact Group	Debit	Credit	Tax Rate Name

    CSVlClean=[]
    try:
        for row in CSVl:
            #print("unclean csv", len(row), row)
            if len(row) > 0 and len(row[0]) > 0 and (row[0] is not None
                and row[0] != '\ufeff'
                and 'Account Transactions' not in row[0]
                and 'Patinio' not in row[0]
                and 'For the period' not in row[0]
                and 'Account Code' not in row[0]
                and 'Accrual Basis' not in row[0]
                and 'Total' not in row[0]
                and '490' not in row[0]
                and '610' not in row[0]
                and '713' not in row[0]
                and '749' not in row[0]
                and '800' not in row[0]
                and '801' not in row[0]
                and '830' not in row[0]
                and '840' not in row[0]
                and '960' not in row[0]):

                #print("..", row)

                row[0] = row[0].replace('\ufeff', '')
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
                row[8] = row[8].replace(",", "")
                row[12] = row[12].replace(",", "")
                row[15] = row[15].replace(",", "")
                row[16] = row[16].replace(",", "")
                # row[8] = float(row[8])
                #if row[14] == '0.0%':
                #     row[14] = '0.00%'

                #if row[0] == '445':
                print("Cleaning xero row..>>", row)
                #print(">>", row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17])
                Cclean=[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]]
                CSVlClean.append(Cclean)

        # for ee in CSVlClean:
        #     print("clean CSV ",ee)
        return(CSVlClean)

    except Exception as mie:
        print("Error 8: The Xero file could not be processed and clean:", mie)
        sys.exit(8)
