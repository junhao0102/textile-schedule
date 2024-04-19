import json
import streamlit as st
from st_aggrid import AgGrid
from streamlit_option_menu import option_menu
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd


from fun import load_sample_data,predict_rotation,predict_linepower,predict_feedyarn,predict_feedoil,machine_order,merge_DF,predict_time,predict_flaw ,load_data,final
from schedule import schedule,schedule_info
current_path = Path(__file__).resolve().parent

# st.set_page_config(layout="wide", page_title='針織機效率與品質導向參數優化模組 ')
# st.header(":blue[針織機效率與品質導向參數優化模組]")
# st.subheader("智慧設備暨系統雲端加值服務技術開發計畫")
# st.markdown("    Copyright © Institute for Information Industry")
# st.markdown(" " )
history, order_data, machine_data = load_sample_data()
df0 = machine_order(machine_data,order_data)
df1 = predict_rotation(history, order_data, machine_data)
df2 = predict_linepower(history, order_data, machine_data)
df3 = predict_feedyarn(history, order_data, machine_data)
df4 = predict_feedoil(history, order_data, machine_data)
data = merge_DF(df0,df1,df2,df3,df4)
st.write(data)
# data= merge_data(df1,df2,df3,df4)
# time = predict_time(history,order_data,data)
# predict_data = predict_flaw(history,time)
# jobs, num_machines, initial_waiting_time = schedule_info(predict_data,machine_data)
# machine_assignments = schedule(jobs, num_machines, initial_waiting_time)
# st.write(final (machine_assignments,data,predict_data))



# user_list = ['範例資料', '自訂資料']
# icon = ['filetype-xlsx', 'cloud-download']
# with st.sidebar:
#     user_menu = option_menu(
#         "Menu", user_list,
#         menu_icon='gear',
#         icons=icon
#     )


# if user_menu == '範例資料':
#     #----系統預設資料頁----
#     history, order_data, machine_data = load_sample_data()
#     with st.expander('#### 點我查看範例資料'):
#         st.info('### 織造紀錄')
#         AgGrid(
#             history.head(10), fit_columns_on_grid_load=True,
#             allow_unsafe_jscode=True,
#             enable_enterprise_modules=True, theme='material')
#         st.info('### 訂單資料')
#         AgGrid(
#             order_data.head(10), fit_columns_on_grid_load=True,
#             allow_unsafe_jscode=True,
#             enable_enterprise_modules=True, theme='material')
#         st.info('### 機台資料')
#         AgGrid(
#             machine_data, fit_columns_on_grid_load=True,
#             allow_unsafe_jscode=True,
#             enable_enterprise_modules=True)
#     st.markdown(" " )
#     st.markdown("""
#                     <style>
#                     div.stButton > button {
#                         width: 300px;
#                         height: 50px;
#                      </style>
#                 """, unsafe_allow_html=True)
#     if st.button('執行優化'):
#         with st.spinner('優化中，請稍後'):
#             df1 = predict_rotation(history, order_data, machine_data)
#             df2 = predict_linepower(history, order_data, machine_data)
#             df3 = predict_feedyarn(history, order_data, machine_data)
#             df4 = predict_feedoil(history, order_data, machine_data)
#             data= merge_data(df1,df2,df3,df4)
#             time = predict_time(history,order_data)
#             st.write(data)
#             predict_data = predict_flaw(history,time)
#             orders, num_machines, initial_waiting_time = schedule_info(predict_data,machine_data)
#             schedule(orders, num_machines, initial_waiting_time)

       
# else:
#     #----自訂資料頁----
#     button_on = False
#     history, order_data, machine_data = load_data()
#     if history is not None and order_data is not None and machine_data is not None:
#         button_on = True
#         st.markdown("""
#                     <style>
#                     div.stButton > button {
#                         width: 300px;
#                         height: 50px;
#                      </style>
#                 """, unsafe_allow_html=True)
#         if st.button('執行優化'):
#             with st.spinner('優化中，請稍後'):
#                 time = predict_time(history,order_data)
#                 predict_data = predict_flaw(history,time)
#                 orders, num_machines, initial_waiting_time = schedule_info(predict_data,machine_data)
#                 schedule(orders, num_machines, initial_waiting_time)
       
        



    







