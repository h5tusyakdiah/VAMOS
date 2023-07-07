import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from dateutil.relativedelta import relativedelta
import datetime as dt
import math
import os

st.set_page_config(page_title="VAMOS", 
                   page_icon=":bar_chart:", 
                   layout="wide")

st.markdown("<h3 style='text-align: center; color: black;'>Vessel Performance</h3>", unsafe_allow_html=True)
#st.markdown("<h5 style='text-align: center; color: black;'>Management System</h5>", unsafe_allow_html=True)
st.text("")
st.text("")


#parameter1
co1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
with co1:
    nama_kapal_input = st.selectbox("Nama Kapal",["KM PUSRI INDONESIA", "KM MOCHTAR PRABU MANGKUNEGARA", "KM ANUGERAH BUANA III"])
with col2:
    LSFO_price = st.number_input("LSFO Price", help="Bahan bakar ketika berlayar", step=1e-6, format="%.1f")
with col3:
    Fuel_Cons1 = st.number_input("Fuel Consumption",value =26,min_value=0, help="xxx")
with col4:
    sailing_days = st.number_input("Sailing Days",min_value=0.0, help="xxx", step=1e-6, format="%.1f")
with col5:
    HSD_Price = st.number_input("HSD Price",value =705,min_value=0, help="xxx")

#parameter part 2
co6, col7, col8, col9, col10 = st.columns([1, 1, 1, 1, 1])
with co6:
    Fuel_Cons2 = st.number_input("Fuel Consumption AE", value=1,min_value=0, help="xxx")
with col7:
    Fixed_Cost = st.number_input("Fixed Cost",value =15125,min_value=0, help="xxx")
with col8:
    Cargo_Volume = st.number_input("Cargo Volume",value =15,min_value=0, help="xxx")
with col9:
    Discharge_rate = st.number_input("Discharge rate",value =4000,min_value=0, help="xxx")
with col10:
    Loading_rate = st.number_input("Loading rate",value =4000,min_value=0, help="xxx")

#parameter part 3

co111, col12, col13, col14, col15 = st.columns([1, 1, 1, 1, 1])
with co111:
    Freight_ton = st.number_input("Freight per ton",value =20.0, min_value=0.0, help="xxx", step=1e-6, format="%.1f")
    

#parameter part 4

co116, col17, col18, col19, col20 = st.columns([1, 1, 1, 1, 1])
with co116:
    cost_realization = st.number_input("Cost Realization",min_value=0.0, help="xxx", step=1e-6, format="%.1f")
with col17:
    budget = st.number_input("Budget",value=1.0, min_value=0.0, help="xxx", step=1e-6, format="%.1f")
with col18:
    variable_cost = st.number_input("Variable Cost",value=1.0, min_value=0.0, help="xxx", step=1e-6, format="%.1f")

#RUN CALCULATION

hitung = st.button("Hitung") 

if hitung:
    data1 = pd.read_csv("dummy simulasi.csv", sep=",")
    data1['Time_arrived'] = pd.to_datetime(data1['Time_arrived'])
    data1['Time_depature'] = pd.to_datetime(data1['Time_depature'])
    data1["operate_day"] = data1["Time_arrived"] - data1["Time_depature"]
    data1["operate_day"] = data1["operate_day"].astype(str)
    data1["operate_day"] = data1["operate_day"].str[:2]

    #menghitung realisasi
    data_filter = data1[(data1.Nama_Kapal == nama_kapal_input)]
    data_filter["operate_day"] = data_filter["operate_day"].astype(int)
    realisasi = data_filter["Time_elapsed"]/data_filter["Time_planned"]
    realisasi = realisasi.sum()

    #menghitung speed
    speed = (data_filter["operate_day"]/data_filter["Standard_time_planned"])*100
    speed = speed.sum()

    #menghitung P & L
    Distance = 1207
    Speed = 14
    sailing_days =  Distance*2/(Speed*24) 
    LSFO_price =  LSFO_price*1.1
    Bunker_Sailing= sailing_days*LSFO_price*Fuel_Cons1*-1
    HSD_Price = HSD_Price*1.1
    Port_Days = (Cargo_Volume/Loading_rate)+(Cargo_Volume/Discharge_rate)
    Bunker_at_Port = HSD_Price*Port_Days*Fuel_Cons2*-1
    Total_Days = Port_Days+sailing_days
    Port_Charges = 2.05*Cargo_Volume*-1
    Total_Fixed_cost = Total_Days*Fixed_Cost*-1 
    Total_cost = Port_Charges+Total_Fixed_cost+Bunker_at_Port+Bunker_Sailing
    Revenue = Cargo_Volume*Freight_ton
    P_and_L = Total_cost+Revenue

    #menghitung Cost Accuracy
    Cost_Accuracy = (cost_realization/budget)*100

    #menghitung BEP
    BEP = P_and_L/(Fixed_Cost-variable_cost)
    
    st.markdown(f"Kapal **{(nama_kapal_input)}** memiliki nilai")


    co1A, colB, colC, colD, colE = st.columns([1, 1, 1, 1, 1])
    co1A.metric(label = "Realisasi",
                value = (f"{round(realisasi,2)} %"))
    colB.metric(label = "Speed",
                value = (f"{round(speed,2)} %"))
    colC.metric(label = "P & L",
                value = (f"Rp. {round(P_and_L)}"))
    colD.metric(label = "Cost_Accuracy",
                value = (f"{round(Cost_Accuracy,2)} %"))
    colE.metric(label = "BEP",
                value = (f"{round(BEP,2)} %"))
    
    #st.markdown(f"realisasi = **{round(realisasi,2)}** %")
    #st.markdown(f"speed = **{round(speed,2)}** %")
    #st.markdown(f"P & L = Rp. **{round(P_and_L)}**")
    #st.markdown(f"Cost_Accuracy = **{round(Cost_Accuracy,2)}** %")
    #st.markdown(f"BEP = **{round(BEP)}** %")
    #st.markdown(f"Bunker_Sailing = **{round(Bunker_Sailing)}**, Port_Days = **{round(Port_Days)}** , Total_cost = **{round(Total_cost)}**  %")


#-----------------
# Disable certificate verification (Not necessary always)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from gspread_pandas import Spread,Client
from google.oauth2 import service_account
# Application Related Module
import pubchempy as pcp
from pysmiles import read_smiles
# 
import networkx as nx


# Create a Google Authentication connection object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope=scope,creds=credentials)
spreadsheetname = "Rekap Vessel Performance"
spread = Spread(spreadsheetname,client = client)

# Check the connection
st.write(spread.url)

sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()


