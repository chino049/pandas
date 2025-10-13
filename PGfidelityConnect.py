import psycopg2

# database="xero", user="xero_user", password="nCircle007", host="localhost", port="5432")
def pgConn(db, db_user, db_pw, db_host, db_port):

    try:
        #Using psql
        conn = psycopg2.connect(database=db, user=db_user, password=db_pw, host=db_host, port=db_port)
        cur = conn.cursor()
        # cur.execute("select * from transaction_detailed")
        # pgl = cur.fetchall()
        #print(type(pgl), pgl)

    except Exception as pp:
        print("ERROR: Cannot connect/login to the database or table", db, pp )
        sys.exit(82)

    return(cur, conn)
    # cur.close()
    #conn.close()


