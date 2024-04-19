from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import pandas as pd

'''
    random_forest: 預測機器的轉數、張力、喂紗量、喂油量(會因為機台不同和布料不同而有所差異  
    linear_regression: 預測機器的織造時間與瑕疵數(機台不同和布料不同大致差不多

'''
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

def linear_regression(history,order_data,features,target):
    predict_df = pd.DataFrame()
    model = LinearRegression()
    X = history[features]
    Y = history[target[0]]
    model.fit(X,Y)
    predict_data = model.predict(order_data[features])
    predict_data = pd.DataFrame(predict_data, columns=target)
    predict_df = pd.concat([predict_df, predict_data],  ignore_index=True)
    return predict_df