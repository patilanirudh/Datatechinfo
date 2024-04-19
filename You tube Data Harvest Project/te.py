from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st

client=pymongo.MongoClient("mongodb+srv://gome4073:Test23@cluster0.kfcmorw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client["Youtube_data"]
def show_channels_table():
    ch_list=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)

    return df

with st.sidebar:
    st.title(":red[YOUTUBE DATA HAVERSTING AND WAREHOUSING]")
    st.header("Skill Take Away")
    st.caption("Python Scripting")
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("API Integration")
    st.caption("Data Management using MongoDB and SQL")

st.title(":red[Details Table]")
show_channels_table()
