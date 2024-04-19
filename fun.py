import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math

from st_aggrid import AgGrid
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error , mean_absolute_error, r2_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from model import random_forest,linear_regression
current_path = Path(__file__).resolve().parent


plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置中文字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号无法显示的问题

# ---- 資料匯入 ----
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
        st.markdown('#### 請上傳織造紀錄資料集')
        uploaded_history = st.file_uploader(
            "", key='history')
        history = upload_data(uploaded_history, 'history')
        st.write('-----------------')
        st.markdown('#### 請上傳訂單資料')
        uploaded_order = st.file_uploader(
            "", key='order')
        order = upload_data(uploaded_order, 'order')
        st.write('-----------------')
        st.markdown('#### 請上傳機台資料:')
        uploaded_machine = st.file_uploader(
            "", key='machine')
        machine = upload_data(uploaded_machine, 'machine')
    return history, order, machine


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
            df_data = None
            st.err('#### 請上傳excel或CSV檔')
    else:
        df_data = None
    return df_data



#----根據機器預測不同機器對不同訂單的轉速---
def predict_rotation(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)', '針數(針/吋)'],['針筒轉數(圈)'])
    return  predict_df
#----根據機器預測不同機器對不同訂單的紗線張力---
def predict_linepower(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)', '聚酯纖維%', '尼龍%', '棉%', '彈性纖維%'],['紗線張力(cN)'])
    return  predict_df
#----根據機器預測不同機器對不同訂單的喂紗率---
def predict_feedyarn(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['織造數量(米)','布重(克/平方米)','丹尼數(D)','針數(針/吋)'],['喂紗率 (米/每分鐘​)'])
    return  predict_df

#----根據機器預測不同機器對不同訂單的喂油量---
def predict_feedoil(history, order_data,machine_data):
    predict_df = pd.DataFrame()
    num_machines = machine_data['機台編號'].unique().size
    predict_df = random_forest(num_machines,history,order_data,['布重(克/平方米)', '丹尼數(D)'],['喂油量 (毫升/小時)'])
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
    # 假設你已經有一個空的 DataFrame，命名為 df
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
    # 在迴圈結束後，再執行合併
    df = pd.merge(df, df, on=['機台編號', '訂單編號'], how='left')
    return df


#----合併----
def merge_DF(df0,df1,df2,df3,df4):
    df = pd.concat([df0,df1,df2,df3,df4],axis=1)
    return  df

#----預測時間----
def predict_time(history,order_data,time):

    #----預測訂單的締造時間和瑕疵數---
    X = history[['織造數量(米)','布重(克/平方米)','丹尼數(D)','針數(針/吋)']]
    Y = history['織造時間(小時)']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train,Y_train)
    time = model.predict(order_data[['織造數量(米)','布重(克/平方米)','丹尼數(D)','針數(針/吋)']])

    #----整合資料----
    time = np.ceil(time)
    time = pd.DataFrame(time, columns=['織造時間(小時)'])
    time = pd.concat([order_data, time], axis=1)
    time["織造時間(天)"] = time["織造時間(小時)"]/24
    time["織造時間(天)"] = time["織造時間(天)"].apply(math.ceil)
    return time


def predict_flaw(history,time):
    X = history[['織造數量(米)','布重(克/平方米)', '丹尼數(D)', '針數(針/吋)','織造時間(小時)']]  
    Y = history['瑕疵數']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train,Y_train)
    flaw = model.predict(time[['織造數量(米)','布重(克/平方米)', '丹尼數(D)', '針數(針/吋)','織造時間(小時)']])

    #----整合資料----
    flaw = np.ceil(flaw)
    flaw = pd.DataFrame(flaw, columns=['瑕疵數'])
    flaw = pd.concat([time, flaw], axis=1)
    return flaw
    
    
#----繪製最後預測參數----    
def final(machine_assignments,merge_data,time):
    # 解析資料，建立字典
    # print(machine_assignments)
    parsed_data = []
    for machine_number ,orders in enumerate(machine_assignments):
        for order in orders:
            parsed_data.append({
                '訂單編號': order['order_number'],
                '機台編號':machine_number+1,
                '幾日後開始生產': order['start_time'],
                '預計織造數量(米)': order['length'],
                '預估織造時間(小時)': order['duration_hour'],
                '預計瑕疵數': order['flaw'],    
            })
                               
    df = pd.DataFrame(parsed_data)
    df = df.sort_values(by=['幾日後開始生產'])
    for index, row in df.iterrows():
        for index2, row2 in merge_data.iterrows(): 
            if row['訂單編號'] == row2['訂單編號'] and row['機台編號'] == row2['機台編號']:
                df.loc[index, '針筒轉數(圈)'] = row2['針筒轉數(圈)']
                df.loc[index, '紗線張力(cN)'] = row2['紗線張力(cN)']
                df.loc[index, '喂紗率 (米/每分鐘​)'] = row2['喂紗率 (米/每分鐘​)']
                df.loc[index, '喂油量 (毫升/小時)'] = row2['喂油量 (毫升/小時)']
    columns = ['訂單編號','機台編號','幾日後開始生產','預計織造數量(米)','針筒轉數(圈)','紗線張力(cN)','喂紗率 (米/每分鐘​)','喂油量 (毫升/小時)','預估織造時間(小時)','預計瑕疵數']
    df = df.reindex(columns=columns)
    return df  




   
        
        
   



 