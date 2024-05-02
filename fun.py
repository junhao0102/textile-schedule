import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math


from pathlib import Path
from model import random_forest,linear_regression
from schedule import schedule,plot_gantt_chart

current_path = Path(__file__).resolve().parent



# ---- 資料匯入 ----
@st.cache_data
def load_sample_data():
    history = pd.read_excel(
            f'{current_path}//sample//history.xlsx',
            engine='openpyxl')
    order_data = pd.read_excel(
            f'{current_path}//sample//order_data.xlsx',
            engine='openpyxl')
    machine_data = pd.read_excel(
            f'{current_path}//sample//machine_state.xlsx',
            engine='openpyxl')
    return history, order_data, machine_data


# --streamlit 資料匯入功能介面--
def load_data():
    with st.expander('#### 點我上傳資料集'):
        st.markdown('#### 請上傳織造紀錄資料集:')
        uploaded_history = st.file_uploader("", key='history')
        st.write('-----------------')
        st.markdown('#### 請上傳訂單資料:')
        uploaded_order = st.file_uploader("", key='order')
        st.write('-----------------')
        st.markdown('#### 請上傳機台資料:')
        uploaded_machine = st.file_uploader("", key='machine')
    return uploaded_history, uploaded_order, uploaded_machine
    


# --- 載入資料 ---
def upload_data(uploaded, fk):
    """_summary_

    Args:
        uploaded : streamlit.file_uploader
        fk (str): key word

    Returns:
        df_data: dataframe or None
    """
    if uploaded is not None:
        file_extension = Path(f'{uploaded.name}').suffix
        if file_extension == '.csv':
            sel_cols = st.columns(4)
            with sel_cols[0]:
                sp_mark = st.selectbox(
                    '分隔符號', [',', '空格', '/', ';', ':'], key=f'mark_{fk}')
            with sel_cols[1]:
                f_encode = st.selectbox(
                    "資料集編碼", ['utf-8', 'Big5', 'cp950'],
                    key=f'encode_{fk}')
            if sp_mark == '空格':
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=' ')
            else:
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=sp_mark)
        elif file_extension in ['.xlsx', '.xls']:
            if file_extension == '.xlsx':
                def_engine = 'openpyxl'
            else:
                def_engine = 'xlrd'
            df_data = pd.read_excel(
                uploaded, engine=def_engine)
        else:
            st.error(f'請輸入正確的檔案格式: csv, xlsx, xls 格式')
            df_data = None
    return df_data

#----根據機器預測不同機器對不同訂單的轉速---
def predict_rotation(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)', '針數(針/吋)'],['針筒轉數(圈)'])
    predict_df = predict_df.round(0)
    return  predict_df
#----根據機器預測不同機器對不同訂單的紗線張力---
def predict_linepower(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)', '聚酯纖維%', '尼龍%', '棉%', '彈性纖維%'],['紗線張力(cN)'])
    predict_df = predict_df.round(1)
    return  predict_df
#----根據機器預測不同機器對不同訂單的喂紗率---
def predict_feedyarn(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['織造數量(米)','布重(克/平方米)','丹尼數(D)','針數(針/吋)'],['喂紗率 (米/每分鐘​)'])
    predict_df = predict_df.round(0)
    return  predict_df

#----根據機器預測不同機器對不同訂單的喂油量---
def predict_feedoil(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)'],['喂油量 (毫升/小時)'])
    predict_df = predict_df.round(1)
    return  predict_df

#----將機器號和訂單數據合併為一個單一的 DataFrame----
def machine_order(machine_data,order_data):
    '''
    EXAMPLE:
                    機台編號  訂單編號
                0      1        101
                1      1        102
                2      1        103
                3      2        101
                4      2        102
                5      2        103
    '''
    df = pd.DataFrame()
    num_machine = machine_data['機台編號'].unique().size
    num_orders = order_data['訂單編號'].unique().size
    df = pd.DataFrame()
    for i in range(1, num_machine + 1):
        append_column = []
        append_column2 = []
        for j in range(1, num_orders + 1):  # 補充機台編號
            append_column.append(i)
        for k in range(0, num_orders):  # 補充訂單編號
            number = order_data.loc[k]["訂單編號"]
            append_column2.append(number)
        # 將新的列添加到 df 中
        df_temp = pd.DataFrame({'機台編號': append_column, '訂單編號': append_column2})
        df = pd.concat([df, df_temp], ignore_index=True)
    # 執行合併
    df = pd.merge(df, df, on=['機台編號', '訂單編號'], how='left')
    return df

#----合併----
def merge_DF(df0,df1,df2,df3,df4):
    df = pd.concat([df0,df1,df2,df3,df4],axis=1)
    return  df

#----預測時間----
def predict_time(history,order_data,df):
    #----預測訂單的締造時間和瑕疵數---
    df = pd.DataFrame()
    df = linear_regression(history,order_data,['織造數量(米)','布重(克/平方米)','丹尼數(D)','針數(針/吋)'],['織造時間(小時)'])
    #----整合資料----
    df = pd.DataFrame(df, columns=['織造時間(小時)'])
    df = pd.concat([order_data, df], axis=1)
    df["織造時間(天)"] = df["織造時間(小時)"]/24
    df["織造時間(天)"] = df["織造時間(天)"].apply(math.ceil)
    return df

#----預測瑕疵數----
def predict_flaw(history,time):
    df = pd.DataFrame()
    df = linear_regression(history,time,['織造數量(米)','布重(克/平方米)', '丹尼數(D)', '針數(針/吋)','織造時間(小時)'],['瑕疵數'])
    #----整合資料----
    df = np.ceil(df)
    df = pd.DataFrame(df, columns=['瑕疵數'])
    df = pd.concat([time, df], axis=1)
    return df
    

#----優化執行----
def optimize(history, order_data, machine_data):
    with st.spinner('優化中，請稍後'):
        try:
            #----資料預測----
            df0 = machine_order(machine_data, order_data)
            df1 = predict_rotation(history, order_data, machine_data)
            df2 = predict_linepower(history, order_data, machine_data)
            df3 = predict_feedyarn(history, order_data, machine_data)
            df4 = predict_feedoil(history, order_data, machine_data)
            #----合併資料----
            merge_data = merge_DF(df0, df1, df2, df3, df4)
            time = predict_time(history, order_data, merge_data)
            predict_data = predict_flaw(history, time)
            #----排程----
            machine_assignments = schedule(predict_data, machine_data)
            result=  dataframe_print(machine_assignments, merge_data)
            plot_gantt_chart(machine_assignments)
            st.write(result)
            return result
        except:
            st.error('預測失敗，請檢察資料是否匹配')
    
        

#----統整dataframe列印----    
def dataframe_print(machine_assignments,merge_data):
    parsed_data = []
    #----將machine_assignments資料取出並整合----
    for machine_number, orders in enumerate(machine_assignments):
        for order in orders:
            parsed_data.append({
                '訂單編號': order['order_number'],
                '機台編號': machine_number + 1,
                '幾日後開始生產': order['start_time'],
                '預計織造數量(米)': round(float(order['length']), 0),
                '預估織造時間(小時)': round(float(order['duration_hour']), 0),
                '預計瑕疵數': round(float(order['flaw']), 0),
            })               
    df = pd.DataFrame(parsed_data)
    #----找出對應的參數並加上----
    for index, row in df.iterrows():
        for index2, row2 in merge_data.iterrows(): 
            if row['訂單編號'] == row2['訂單編號'] and row['機台編號'] == row2['機台編號']:
                df.loc[index, '針筒轉數(圈)'] = row2['針筒轉數(圈)']
                df.loc[index, '紗線張力(cN)'] = row2['紗線張力(cN)']
                df.loc[index, '喂紗率 (米/每分鐘​)'] = row2['喂紗率 (米/每分鐘​)']
                df.loc[index, '喂油量 (毫升/小時)'] = row2['喂油量 (毫升/小時)']
    columns = ['訂單編號','機台編號','幾日後開始生產','預計織造數量(米)','針筒轉數(圈)','紗線張力(cN)','喂紗率 (米/每分鐘​)','喂油量 (毫升/小時)','預估織造時間(小時)','預計瑕疵數']
    df = df.reindex(columns=columns)
    df = df.sort_values(by=['幾日後開始生產'])
    effiefficient(df)
    return df 

#----效率計算----
def effiefficient(df):
    total_length = df['預計織造數量(米)'].sum()
    total_time = df['預估織造時間(小時)'].sum()
    total_flaw = df['預計瑕疵數'].sum()
    efficiency = float(total_length / total_time)
    flaw_rate = float(total_flaw / (total_length/1000))
    efficiency_text = f"<span style='color: green; font-size:24px'>優化後效率: {format(efficiency, '.2f')} 米/小時</span>"
    flaw_rate_text = f"<span style='color: green ; font-size:24px'>優化後瑕疵率 : {format(flaw_rate, '.2f')} 瑕疵數/千米</span>"
    st.markdown(efficiency_text, unsafe_allow_html=True)
    st.markdown(flaw_rate_text, unsafe_allow_html=True)
    return efficiency,flaw_rate

   
        
        
   



 