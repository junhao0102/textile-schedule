import streamlit as st
from st_aggrid import AgGrid
from streamlit_option_menu import option_menu
from pathlib import Path

from fun import load_sample_data,load_data,optimize,upload_data

current_path = Path(__file__).resolve().parent

st.set_page_config(layout="wide", page_title='針織機效率與品質導向參數優化模組 ')
st.header(":blue[針織機效率與品質導向參數優化模組](Full)")
st.subheader("智慧設備暨系統雲端加值服務技術開發計畫")
st.markdown("    Copyright © Institute for Information Industry")
st.markdown(" " )




user_list = ['範例資料', '自訂資料']
icon = ['filetype-xlsx', 'cloud-download']
with st.sidebar:
    user_menu = option_menu(
        menu_title="選擇項目",  
        options=user_list, 
        icons=icon,        
        menu_icon='list'    
    )


if user_menu == '範例資料':
    #----系統預設資料頁----
    history, order_data, machine_data = load_sample_data()
    with st.expander('#### 點我查看範例資料'):
        st.info('### 織造紀錄')
        AgGrid(
            history.head(10), fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True, theme='material')
        st.info('### 訂單資料')
        AgGrid(
            order_data.head(10), fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True, theme='material')
        st.info('### 機台資料')
        AgGrid(
            machine_data, fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True)
    st.markdown(" " )
    st.markdown("""
                    <style>
                    div.stButton > button {
                        width: 300px;
                        height: 50px;
                     </style>
                """, unsafe_allow_html=True)
    if st.button('執行優化'):
            optimize(history, order_data, machine_data)

       
else:
    #----自訂資料頁----
    button_on = False
    uploaded_history, uploaded_order, uploaded_machine = load_data()
    if uploaded_history is not None and uploaded_order is not None and uploaded_machine is not None:
        button_on = True
        st.markdown("""
                    <style>
                    div.stButton > button {
                        width: 300px;
                        height: 50px;
                     </style>
                """, unsafe_allow_html=True)
        if st.button('執行優化'):
            with st.spinner('資料上傳中，請稍後'):
                    history = upload_data(uploaded_history, 'history')
                    order_data = upload_data(uploaded_order, 'order')
                    machine_data = upload_data(uploaded_machine, 'machine') 
            if history is not None and order_data is not None and machine_data is not None:   
                optimize(history, order_data, machine_data)
            
    else:
        st.info('請上傳所有必要的檔案。')
                
                
                
       
        



    







