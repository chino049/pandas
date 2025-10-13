import sys
from datetime import datetime


def cleanFidelityCSVfile(CSVl):
    #print("CSVl", CSVl)
    CSVlClean=[]
    try:
        for rda in CSVl:
            print(".", len(rda))
            if len(rda) > 0 :
                if 'Date downloaded' in rda[0]:
                    print("2")
                    dateDownloaded = rda[0].split('Date downloaded ')
                    print("3", dateDownloaded[1])
                    dateSplit = dateDownloaded[1].split()
                    print("4", dateSplit)
                    # recordDate = dateSplit[0]
                    print('date is', dateSplit[0])
                    pos_date = datetime.strptime(dateSplit[0], ('%m/%d/%Y'))

        for row in CSVl:
            print("unclean fidelity csv", row)
            # old
            # "Z21480840"	"Trust: Under Agreement"	"BDC"	"BELDEN INC"	129
            # "$76.30"	"$2.86"	"$9,842.70"	"$368.94 "	"3.89%"	"$2,955.39 "	"42.91%"	"29.76%"	"$6,887.31 "	"$53.39 "	"Cash"

            # new
            # Z21480840,    Trust: Under Agreement,   ,BDC,      BELDEN INC,      129,
            # $94.87,   -$0.30,  $12238.23, -$38.70,    -0.32 %, +$5350.92,      +77.69 %,    34.23 %,    $6887.31,     $53.39,      Cash

            # cleaning[ 'Z21480840', 'Trust: Under Agreement', '', 'PLUG', 'PLUG POWER INC', '111',
            # '$9.98', '-$0.59', '$1107.78', '-$65.49', '-5.59%', '+$711.33', '+179.42%', '3.10%', '$396.45', '$3.57', 'Cash']
            # Error 88: The Fidelity file could not be processed and clean: could not convert string to float: '3.10%'


            if len(row) > 0 and len(row[0]) > 0 and ('Account Number' not in row[0]
                                and 'The data and information' not in row[0]
                                and 'Brokerage services' not in row[0]
                                and 'Date downloaded' not in row[0]) :
                if 'FCASH**' not in row[2] and 'CORE**' not in row[2] and 'FDRXX**' not in row[2] and 'Pending Activity' not in row[2]:
                    print("JOP 135: cleaning", row)



                    row[0] = row[0].replace('\ufeff', '')

                    for i in range(0,len(row)):
                        row[i] = row[i].replace("%", "")
                        row[i] = row[i].replace("$", "")
                        row[i] = row[i].replace(",", "")
                        # row[i] = row[i].replace(")", "")
                        # row[i] = row[i].replace("(", "-")
                        print("clean field", row[i])

                    #row[5] = row[5].replace(",", "")
                    #row[5] = float(row[5])


                    # row[6] = row[6].replace("$", "")
                    # row[6] = row[6].replace(",", "")
                    # row[6] = float(row[6])
                    #
                    # row[7] = row[7].replace("$", "")
                    # row[7] = row[7].replace(")", "")
                    # row[7] = row[7].replace("(", "-")
                    # row[7] = row[7].replace(",", "")
                    # row[7] = float(row[7])
                    #
                    # row[8] = row[8].replace("$", "")
                    # row[8] = row[8].replace(")", "")
                    # row[8] = row[8].replace("(", "-")
                    # row[8] = row[8].replace(",", "")
                    # row[8] = float(row[8])
                    #
                    # row[9] = row[9].replace("$", "")
                    # row[9] = row[9].replace(")", "")
                    # row[9] = row[9].replace("(", "-")
                    # row[9] = row[9].replace(",", "")
                    # row[9] = float(row[9])
                    #
                    # row[10] = row[10].replace("%", "")
                    # row[10] = row[10].replace(",", "")
                    # row[10] = float(row[10])
                    #
                    # row[11] = row[11].replace("$", "")
                    # row[11] = row[11].replace(")", "")
                    # row[11] = row[11].replace("(", "-")
                    # row[11] = row[11].replace(",", "")
                    # row[11] = float(row[11])
                    #
                    # row[12] = row[12].replace("%", "")
                    # row[12] = row[12].replace(",", "")
                    # row[12] = float(row[12])
                    #
                    # row[13] = row[13].replace("$", "")
                    # row[13] = row[13].replace(",", "")
                    # row[13] = float(row[13])
                    #
                    # row[14] = row[14].replace("$", "")
                    # row[14] = row[14].replace(",", "")
                    # row[14] = float(row[14])
                    #
                    # row[15] = row[15].replace("%", "")
                    # row[15] = row[15].replace(",", "")
                    # row[15] = float(row[15])

                    #skipping row 2
                    Cclean=[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], pos_date]

                    CSVlClean.append(Cclean)

        for ee in CSVlClean:
            print("clean CSV ",ee)
        return(CSVlClean)

    except Exception as ie:
        print("Error 88: The Fidelity file could not be processed and clean:", ie)
        sys.exit(88)
