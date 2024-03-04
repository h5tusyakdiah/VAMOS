import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook
import datetime
now_datetime = datetime.datetime.now()

st.set_page_config(page_title="VAMOS", 
                   page_icon=":bar_chart:", 
                   layout="wide")

#-----------
#Sidebar. Packages custom tampilan
import os
from PIL import Image
from streamlit_option_menu import option_menu
    
#input data
Vessel_List = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='Vessel List')
OD_Matrix = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='OD Matrix')
Time_Sheet = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='Input - Time Sheet')
Scheduled = pd.read_excel('Rekap Vessel Performance.xlsx', sheet_name='Scheduled')

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
    sub1, sub2 = st.tabs(["Voyage Progress", "Scheduled"])
# ============================= Submenu Simulation - Equipment =================================
    with sub1:

        #st.markdown("<h3 style='text-align: center; color: black;'>Vessel Performance</h3>", unsafe_allow_html=True)
        st.text("")
        st.text("")

        df = Time_Sheet.drop_duplicates(subset=['Vessel_Name', 'PoL', 'PoD', 'Voyage'])
        df = df [['Status','Vessel_Name', 'PoL', 'PoD', 'Voyage']]
        df = df.assign(
            Freight_ton=415000,
            COB=7000,
            Discharge_rate=4000,
            Loading_rate=2400,
            Freetime_1=2,
            Freetime_2=1,
            Fixed_Cost=30000000,
            ME_Fuel_Cons=12,
            AE_Fuel_Cons=1.4,
            Port_Charges=60000000,
            LSFO_Price=19700,
            HSD_Price=20700
            
        )

         # Membuat DataFrame dari data
        df_input = pd.DataFrame(df)
  
        edit_df = st.data_editor(df_input)
        
        #RUN CALCULATION

        hitung = st.button("Run Calculation") 

        if hitung:
            bunga = edit_df
            def calculate_metrics(row):
                PoL_PoD = OD_Matrix[(OD_Matrix.port1 == row['PoL']) & (OD_Matrix.port2 == row['PoD'])]
                Distance = PoL_PoD.distance.sum()
            
                Sailing_Days = Time_Sheet[(Time_Sheet.Vessel_Name == row['Vessel_Name']) & (Time_Sheet.PoL == row['PoL']) 
                                        & (Time_Sheet.PoD == row['PoD']) & (Time_Sheet.Voyage == row['Voyage'])]
                Sailing_Days = Sailing_Days[(Sailing_Days.Activity == "Sailing to PoD")]
                Sailing_Days = Sailing_Days.Dur.sum()
                
                Port_Days= Time_Sheet[(Time_Sheet.Vessel_Name == row['Vessel_Name']) & (Time_Sheet.PoL == row['PoL']) 
                                        & (Time_Sheet.PoD == row['PoD']) & (Time_Sheet.Voyage == row['Voyage'])]
                Port_Days = Port_Days[(Port_Days.Activity == "Loading") | (Port_Days.Activity == "Discharge")]
                Port_Days = Port_Days.Dur.sum()

                Waiting_Days = Time_Sheet[(Time_Sheet.Vessel_Name == row['Vessel_Name']) & (Time_Sheet.PoL == row['PoL']) 
                                        & (Time_Sheet.PoD == row['PoD']) & (Time_Sheet.Voyage == row['Voyage'])]
                Waiting_Days = Waiting_Days[(Waiting_Days.Activity == "Waiting Loading") | (Waiting_Days.Activity == "Waiting Discharge")]
                Waiting_Days = Waiting_Days.Dur.sum()

                Total_Days = Time_Sheet[(Time_Sheet.Vessel_Name == row['Vessel_Name']) & (Time_Sheet.PoL == row['PoL']) 
                                        & (Time_Sheet.PoD == row['PoD']) & (Time_Sheet.Voyage == row['Voyage'])]
                Total_Days = Total_Days.Dur.sum()

                Bunker_Sailing = (Sailing_Days * row['LSFO_Price'] * row['AE_Fuel_Cons'] * 1000) + (Sailing_Days * row['LSFO_Price'] * row['ME_Fuel_Cons'] * 1000) * -1    
                Bunker_at_Port = (Port_Days* row['HSD_Price'] * row['AE_Fuel_Cons']*1000*2*-1)   
                Bunker_Waiting = (Waiting_Days * row['HSD_Price'] * row['AE_Fuel_Cons']*1000*-1)
                Total_Fixed_cost = Total_Days*row['Fixed_Cost']*-1
                Total_cost = Bunker_Sailing + Bunker_at_Port + Bunker_Waiting + row['Port_Charges'] + Total_Fixed_cost
                Revenue = row['Freight_ton']*row['COB']
                P_and_L = Revenue + Total_cost

                ## IDEAL ###
                
                Distance_2 = Distance 
                filter_ideal =  Vessel_List[(Vessel_List.Nama_Kapal == row['Vessel_Name'])]
                Service_speed_2 = filter_ideal.Speed_Max.sum()
                Sailing_Days_2 =(Distance_2*2)/(Service_speed_2*24)
                Port_Days_2 = (row['COB']/row['Loading_rate'])+(row['COB']/row['Discharge_rate'])
                Waiting_Days_2 = 0
                Total_Days_2 = Sailing_Days_2+Port_Days_2 + Waiting_Days_2
                ME_Fuel_Cons_2 = filter_ideal.ME_Cons.sum()
                AE_Fuel_Cons_2 = filter_ideal.AE_Cons.sum()
                Bunker_Sailing_2 = ((Sailing_Days_2*row['LSFO_Price']*ME_Fuel_Cons_2*1000)+(Sailing_Days_2*row['LSFO_Price']*AE_Fuel_Cons_2*1000))*-1
                Bunker_at_Port_2 = (Port_Days_2*row['HSD_Price']*AE_Fuel_Cons_2*1000*2*-1)
                Bunker_Waiting_2 = (Waiting_Days_2*row['HSD_Price']*AE_Fuel_Cons_2*1000*-1)

                Port_Charges_2 = 8000*row['COB']*-1
                Fixed_Cost_2 = 815000000/30
                Total_Fixed_cost_2 = Total_Days_2*Fixed_Cost_2*-1
                Total_cost_2 = Bunker_Sailing_2 + Bunker_at_Port_2 + Bunker_Waiting_2 + Port_Charges_2 + Total_Fixed_cost_2

                #----------------------------------------------------------------------------
                Remaining_Time	= Total_Days_2 - Total_Days
                Time_accuracy =  Total_Days_2/Total_Days*100
                Speed = Sailing_Days_2/Sailing_Days *100
                P_and_L_actual	= P_and_L
                Cost_accuracy  = Total_cost/Total_cost_2 *100
            
                return pd.Series([Remaining_Time, Time_accuracy, Speed, P_and_L_actual,Cost_accuracy ])

            bunga[[ 'Remaining_Time', 'Time_accuracy', 'Speed', 'P_and_L_actual', 'Cost_accuracy']] = bunga.apply(calculate_metrics, axis=1)
            
            # Menampilkan hasil perhitungan
            bunga_display = bunga[['Vessel_Name', 'PoL', 'PoD', 'Voyage', 'Remaining_Time', 'Time_accuracy', 'Speed', 'P_and_L_actual', 'Cost_accuracy']]
            st.write(bunga_display)

            st.write("<span style='color:red;'>Data berhasil diperbarui!</span>", unsafe_allow_html=True)
            url = "https://tableau.pupuk-indonesia.com/#/views/DashboardVesselPerformance/Dashboard1"
            #st.markdown(f"Executive Dashboard Monitoring [:bar_chart:](%s)" % url)
            st.markdown(f"<span style='font-size: 20px;'>Executive Dashboard Monitoring [:bar_chart:]({url})</span>", unsafe_allow_html=True)


# ============================= Submenu Simulation - Equipment =================================
    with sub2:
        def color_status(val):
            color = 'green' if val == 'Confirm' else 'orange' if val == 'Adm' else 'black'
            return 'color: %s' % color

        # Menerapkan fungsi ke DataFrame
        styled_df = Scheduled.style.applymap(color_status, subset=['Status'])

        st.write(styled_df)
        st.text("")
        st.text("")
