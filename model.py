from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import pandas as pd
# Define the model
def random_forest(num_machine,history,order_data,features,target):
    predict_df = pd.DataFrame()
    for i in range(1,num_machine+1):
        df = history[history['機台編號'] == i]
        model = RandomForestRegressor(max_depth=5, random_state=0, n_estimators=100)
        X = df[features]
        Y = df[target[0]] 
        model.fit(X, Y)
        predict_data = model.predict(order_data[features])
        predict_data = pd.DataFrame(predict_data, columns=target)
        predict_df = pd.concat([predict_df, predict_data],  ignore_index=True)
    return predict_df

def linear_regression(num_machine,history,order_data,features,target):
    predict_df = pd.DataFrame()
    for i in range(1,num_machine+1):
        df = history[history['機台編號'] == i]
        model = LinearRegression()
        X = df[features]
        Y = df[target[0]] 
        model.fit(X, Y)
        predict_data = model.predict(order_data[features])
        predict_data = pd.DataFrame(predict_data, columns=target)
        predict_df = pd.concat([predict_df, predict_data],  ignore_index=True)
    return predict_df