import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook
import datetime

st.set_page_config(page_title="VAMOS", 
                   page_icon=":bar_chart:", 
                   layout="wide")

#-----------
#Sidebar. Packages custom tampilan
import os
from PIL import Image
from streamlit_option_menu import option_menu

with st.sidebar:
    directory_path = os.path.dirname(__file__)
    image = Image.open(os.path.join(directory_path, 'vamos2.png'))
    pad1, pad2, pad3 = st.columns([1,8,1])

    with pad2:
        st.image(image, output_format='png', width=170)
    
    #---MENU
    selected = option_menu("", ['Vessel Performance',"Vessel Selection"], 
    icons=['graph', 'graph'], menu_icon="cast", default_index=0)
    

# IF HOME
if selected == "Vessel Performance":
    st.markdown("<h3 style='text-align: center; color: black;'>Vessel Performance</h3>", unsafe_allow_html=True)
    #st.markdown("<h5 style='text-align: center; color: black;'>Management System</h5>", unsafe_allow_html=True)
    st.text("")
    st.text("")

    #parameter1
    col0, col00, col000, col0000, col00000 = st.columns([1, 1, 1, 1, 1])
    with col0:
        nama_kapal_input = st.selectbox("Ship Class",["KM Pusri Indonesia 1", "KM Julianto Moeliodihardjo"])
    with col00:
        loading_port = st.selectbox("Loading Port",["Banyuwangi", "Belawan", "Bengkulu","Bontang","Cigading",
                                                    "Cilacap","Dumai","Gresik","Lampung","Lembar", "Lhokseumawe",
                                                    "Makassar","Padang","Palembang","Semarang","Sorong","Surabaya"])
    with col000:
        discharge_port = st.selectbox("Discharge Port",["Banyuwangi", "Belawan", "Bengkulu","Bontang","Cigading",
                                                    "Cilacap","Dumai","Gresik","Lampung","Lembar", "Lhokseumawe",
                                                    "Makassar","Padang","Palembang","Semarang","Sorong","Surabaya"])
    with col0000:
        voyage = st.selectbox("Voyage",[1, 2, 3, 4, 5, 6 , 7 , 8 ,  9 , 10])

    co1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with co1:
        Freight_ton = st.number_input("Freight per ton", value = 415000.0, min_value=0.0, help="xxx", step=1e-6, format="%.1f")
    with col2:
        COB = st.number_input("COB", help="Bahan bakar ketika berlayar", value=7000.0, step=1e-6, format="%.1f")
    with col3:
        Discharge_rate = st.number_input("Discharge rate",value =4000,min_value=0, help="xxx")
    with col4:
        Loading_rate = st.number_input("Loading rate",value =2400,min_value=0, help="xxx")
    with col5:
        Freetime_1 = st.number_input("Free Time at PoL", value=0,min_value=0, help="xxx")

    #parameter part 2
    col6, col7, col8, col9, col10 = st.columns([1, 1, 1, 1, 1])
    with col6:
        Freetime_2 = st.number_input("Free Time at PoD", value=0,min_value=0, help="xxx")
    with col7:
        Fixed_Cost = st.number_input("Fixed Cost", value=30000000,min_value=0, help="xxx")
    with col8:
        ME_Fuel_Cons = st.number_input("ME Fuel Cons",value =12,min_value=0, help="xxx")
    with col9:
        AE_Fuel_Cons = st.number_input("AE Fuel Cons",value =1.4,min_value=0.0, help="xxx", step=1e-6, format="%.1f")
    with col10:
        Port_Charges = st.number_input("Port Charges",value =60000000,min_value=0, help="xxx")   

    #parameter part 3

    co111, col12, col13, col14, col15 = st.columns([1, 1, 1, 1, 1])
    with co111:
        LSFO_Price = st.number_input("LSFO Price", value=19700,min_value=0, help="LSFO or HSD")
    with col12:
        HSD_Price = st.number_input("HSD Price", value=20700,min_value=0, help="xxx")

    #RUN CALCULATION

    hitung = st.button("Run Calculation") 

    if hitung:
        
        #input data
        Vessel_List = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='Vessel List')
        OD_Matrix = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='OD Matrix')
        Time_Sheet = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='Input - Time Sheet')

        #calculating
    #ACTUAL
        PoL_PoD = OD_Matrix[(OD_Matrix.port1 == loading_port) & (OD_Matrix.port2 == discharge_port)]
        Distance = PoL_PoD.distance.sum()

        Service_speed = 6.7
        Sailing_Days = Time_Sheet[(Time_Sheet.Vessel_Name == nama_kapal_input) & (Time_Sheet.PoL == loading_port) 
                                & (Time_Sheet.PoD == discharge_port) & (Time_Sheet.Voyage == voyage)]
        Sailing_Days = Sailing_Days[(Sailing_Days.Activity == "Sailing to PoD")]
        Sailing_Days = Sailing_Days.Dur.sum()

        Port_Days= Time_Sheet[(Time_Sheet.Vessel_Name == nama_kapal_input) & (Time_Sheet.PoL == loading_port) 
                                & (Time_Sheet.PoD == discharge_port) & (Time_Sheet.Voyage == voyage)]
        Port_Days = Port_Days[(Port_Days.Activity == "Loading") | (Port_Days.Activity == "Discharge")]
        Port_Days = Port_Days.Dur.sum()

        Waiting_Days = Time_Sheet[(Time_Sheet.Vessel_Name == nama_kapal_input) & (Time_Sheet.PoL == loading_port) 
                                & (Time_Sheet.PoD == discharge_port) & (Time_Sheet.Voyage == voyage)]
        Waiting_Days = Waiting_Days[(Waiting_Days.Activity == "Waiting Loading") | (Waiting_Days.Activity == "Waiting Discharge")]
        Waiting_Days = Waiting_Days.Dur.sum()

        Total_Days = Time_Sheet[(Time_Sheet.Vessel_Name == nama_kapal_input) & (Time_Sheet.PoL == loading_port) 
                                & (Time_Sheet.PoD == discharge_port) & (Time_Sheet.Voyage == voyage)]
        Total_Days = Total_Days.Dur.sum()
        #Sailing_Days, Port_Days, Waiting_Days, Total_Days
        Bunker_Sailing = (Sailing_Days*LSFO_Price*AE_Fuel_Cons*1000)+(Sailing_Days*LSFO_Price*ME_Fuel_Cons*1000)*-1
        Bunker_at_Port = (Port_Days*HSD_Price*AE_Fuel_Cons*1000*2*-1)
        Bunker_Waiting = (Waiting_Days*HSD_Price*AE_Fuel_Cons*1000*-1)
        #Bunker_Sailing, Bunker_at_Port, Bunker_Waiting

        Total_Fixed_cost = Total_Days*Fixed_Cost*-1
        Total_cost = Bunker_Sailing + Bunker_at_Port + Bunker_Waiting + Port_Charges + Total_Fixed_cost
        Revenue = Freight_ton*COB
        P_and_L = Revenue + Total_cost

        #-------------------------------------------------------------------
        #IDEAL
        Distance_2 = Distance 
        filter_ideal =  Vessel_List[(Vessel_List.Nama_Kapal == nama_kapal_input)]
        Service_speed_2 = filter_ideal.Speed_Max.sum()
        Sailing_Days_2 =(Distance_2*2)/(Service_speed_2*24)
        Port_Days_2 = (COB/Loading_rate)+(COB/Discharge_rate)
        Waiting_Days_2 = 0
        Total_Days_2 = Sailing_Days_2+Port_Days_2 + Waiting_Days_2
        ME_Fuel_Cons_2 = filter_ideal.ME_Cons.sum()
        AE_Fuel_Cons_2 = filter_ideal.AE_Cons.sum()
        Bunker_Sailing_2 = ((Sailing_Days_2*LSFO_Price*ME_Fuel_Cons_2*1000)+(Sailing_Days_2*LSFO_Price*AE_Fuel_Cons_2*1000))*-1
        Bunker_at_Port_2 = (Port_Days_2*HSD_Price*AE_Fuel_Cons_2*1000*2*-1)
        Bunker_Waiting_2 = (Waiting_Days_2*HSD_Price*AE_Fuel_Cons_2*1000*-1)

        Port_Charges_2 = 8000*COB*-1
        Fixed_Cost_2 = 815000000/30
        Total_Fixed_cost_2 = Total_Days_2*Fixed_Cost_2*-1
        Total_cost_2 = Bunker_Sailing_2 + Bunker_at_Port_2 + Bunker_Waiting_2 + Port_Charges_2 + Total_Fixed_cost_2
        Revenue_2 = Freight_ton*COB
        P_and_L_2 = Revenue_2 + Total_cost_2
    #----------------------------------------------------------------------------
        Remaining_Time	= Total_Days_2 - Total_Days
        Time_accuracy =  Total_Days_2/Total_Days*100
        Speed = Sailing_Days_2/Sailing_Days *100
        P_and_L_actual	= P_and_L
        Cost_accuracy  = Total_cost/Total_cost_2 *100

        #Output
        #st.markdown(f"Kapal **{(nama_kapal_input)}** memiliki nilai")
        #st.markdown(f"nilai **{(Bunker_Sailing)}**, **{(Bunker_at_Port)}**, **{(Bunker_Waiting)}**")

        #co1A, colB, colC, colD, colE = st.columns([1, 1, 1, 1, 1])
        #co1A.metric(label = "Remaining Time",
        #            value = (f"{round(Remaining_Time,2)}"))
        #colB.metric(label = "Time accuracy",
        #            value = (f"{round(Time_accuracy,2)} %"))
        #colC.metric(label = "Speed",
        #            value = (f"{round(Speed)} %"))
        #colD.metric(label = "P & L",
        #            value = (f"Rp. {round(P_and_L_actual)}"))
        #colE.metric(label = "Cost Accuracy",
        #            value = (f"{round(Cost_accuracy,2)} %"))
        
        url = "https://batics.pupuk-indonesia.com/"
        st.markdown(f"Lihat hasil disini [link](%s)" % url)
        

# IF DATASET
elif selected == "Vessel Selection":
    nama_kapal_input = "KM Julianto Moeliodihardjo"
    st.markdown("<h3 style='text-align: center; color: black;'>Vessel Selection</h3>", unsafe_allow_html=True)
    #st.markdown("<h5 style='text-align: center; color: black;'>Management System</h5>", unsafe_allow_html=True)
    st.text("")
    st.text("")

    #parameter1
    col0, col00, col000, col0000, col00000 = st.columns([1, 1, 1, 1, 1])
    with col0:
        loading_port = st.selectbox("Loading Port",["Banyuwangi", "Belawan", "Bengkulu","Bontang","Cigading",
                                                    "Cilacap","Dumai","Gresik","Lampung","Lembar", "Lhokseumawe",
                                                    "Makassar","Padang","Palembang","Semarang","Sorong","Surabaya"])
    with col00:
        discharge_port = st.selectbox("Discharge Port",["Banyuwangi", "Belawan", "Bengkulu","Bontang","Cigading",
                                                    "Cilacap","Dumai","Gresik","Lampung","Lembar", "Lhokseumawe",
                                                    "Makassar","Padang","Palembang","Semarang","Sorong","Surabaya"])
    with col000:
        berat_ton = st.number_input("Berat", value =0,min_value=0, help="Ton")
    with col0000:
        loading_date = st.date_input( "Loading Date", datetime.date(2023, 7, 6))

    co1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with co1:
        Freight_ton = st.number_input("Freight per ton", value = 415000.0, min_value=0.0, help="xxx", step=1e-6, format="%.1f")
    with col2:
        COB = st.number_input("COB", help="Bahan bakar ketika berlayar", value=7000.0, step=1e-6, format="%.1f")
    with col3:
        Fixed_Cost = st.number_input("Fixed Cost", value=30000000,min_value=0, help="xxx")
    with col4:
        ME_Fuel_Cons = st.number_input("ME Fuel Cons",value =12,min_value=0, help="xxx")
    with col5:
        AE_Fuel_Cons = st.number_input("AE Fuel Cons",value =1.4,min_value=0.0, help="xxx", step=1e-6, format="%.1f")


    #parameter part 2
    col6, col7, col8, col9, col10 = st.columns([1, 1, 1, 1, 1])
    with col6:
        Port_Charges = st.number_input("Port Charges",value =60000000,min_value=0, help="xxx")  
    with col7:
        LSFO_Price = st.number_input("LSFO Price", value=19700,min_value=0, help="LSFO or HSD")
    with col8:
        HSD_Price = st.number_input("HSD Price", value=20700, min_value=0, help="xxx")


    #parameter part 3

    #co111, col12, col13, col14, col15 = st.columns([1, 1, 1, 1, 1])
    #with co111:
    #    LSFO_Price = st.number_input("LSFO Price", value=19700,min_value=0, help="LSFO or HSD")
    #with col12:
    #    HSD_Price = st.number_input("HSD Price", value=20700,min_value=0, help="xxx")

    #RUN CALCULATION

    hitung = st.button("Run Calculation") 

    if hitung:
    
        
        url = "https://batics.pupuk-indonesia.com/"
        st.markdown(f"Lihat hasil disini [link](%s)" % url)
        
