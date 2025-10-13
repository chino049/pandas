
import streamlit as st
import pandas as pd
import psycopg2
import plotly
import plotly.graph_objs as go
import plotly.express as px

def readFile():
    #print("Str5eamlit")
    st.header("Line Chart")
    conn = psycopg2.connect(database="fidelity", user="xero_user", password="nCircle007", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT rec_date ,last_price FROM positions WHERE "
                "rec_date >= timestamp with time zone '2022-01-01 00:00:00.000-08:00' \
                AND rec_date < timestamp with time zone '2025-01-01 00:00:00.000-08:00' "
                "and symbol = 'B:BDC'\
         ")
    pgl = cur.fetchall()
    #print(pgl)
    xx1 = []
    yy1 = []

    # print(type(pgl1), pgl1)
    for rr in pgl:
        # print(".", rrr)
        xx1.append(rr[0])
        yy1.append(rr[1])
    print(xx1)

    # plt.set_xlabel('X LABEL')
    fig = px.line(x=xx1, y=yy1, color_discrete_sequence=['blue'],
        labels = {
                 "x": "Date",
                 "y": "Last Price",

                },
        title = "Belden "
    )
    # fig.x
    # set_xlabel('X LABEL')
    # fig.set_ylabel('Y LABEL')
    #fig.update_layout(width=1300, height=500, bargap=0.05)
    fig

    # for rr in pgl:
    #     print(rr)

    # dafr = pd.DataFrame(pgl)
    # dafr.columns = ["rec_date", "last_price"]
    # dafr
    # st.line_chart(dafr)

    # ax = dafr.plot()
    # ax.set_xlabel("last price")
    # ax.set_ylabel("rec_date")
    # ax.bar_chart()
    #st.line_chart(data=dafr)

    # data = {"a": [23, 12, 78, 4, 54], "b": [0, 13, 88, 1, 3],
    #         "c": [45, 2, 546, 67, 56]}
    #
    # df = pd.DataFrame(data)
    # df
    # st.line_chart(data=df)
    # st.bar_chart(data=df)
    # st.area_chart(data=df)

if __name__ == '__main__':
    readFile()

# streamlit run /home/jordonez/bitbucket/pandas/koy.py --theme.base dark



