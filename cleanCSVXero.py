import sys
from datetime import datetime

def cleanXeroCSVfile(CSVl):

    CSVlClean=[]
    try:
        for row in CSVl:
            print("unclean csv", len(row), row)
            if len(row) > 0 and len(row[0]) > 0 and (row[0] is not None and row[0] != '\ufeff'
                and 'Detailed Account' not in row[0]
                and 'Patinio' not in row[0]
                and 'From' not in row[0]
                and 'Account Code' not in row[0]
                and 'Total' not in row[0]):

                row[0] = row[0].replace('\ufeff', '')
                row[4] = row[4].replace("\\", "").replace('"', '').replace("\n", "").replace("\r", "")
                row[2] = datetime.strptime(row[2], '%d/%m/%Y')
                row[2] = datetime.strftime(row[2], '%Y-%m-%d')
                row[6] = row[6].replace("₱", "")
                row[6] = row[6].replace(",", "")
                row[6] = float(row[6])
                row[7] = row[7].replace("₱", "")
                row[7] = row[7].replace(",", "")
                row[7] = float(row[7])
                row[8] = row[8].replace("₱", "")
                row[8] = row[8].replace(",", "")
                row[8] = float(row[8])
                if row[9] == '0.0%':
                    row[9] = '0.00%'
                #print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
                Cclean=[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]
                CSVlClean.append(Cclean)

        # for ee in CSVlClean:
        #     print("clean CSV ",ee)
        return(CSVlClean)

    except Exception as mie:
        print("Error 8: The Xero file could not be processed and clean:", mie)
        sys.exit(8)
