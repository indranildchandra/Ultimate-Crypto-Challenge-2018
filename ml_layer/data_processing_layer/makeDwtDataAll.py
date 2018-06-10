import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pywt
import json
import pandas as pd
import math

import tqdm

WINDOW_SIZE = 24*10
TRAIN_TEST_SPLIT = 1.0

df_data = pd.read_csv('bitcoin_historical_hourly_data.csv',sep=',')
data = df_data.as_matrix()
# data = np.loadtxt('bitcoin_historical_hourly_data.csv',delimiter=',')

def fitScaler(data):
	scaler = MinMaxScaler()
	scaler.fit(data)
	return scaler

def normalize_data(data, scaler):
	new_data = scaler.transform(data)
	return new_data

train_index = math.floor(TRAIN_TEST_SPLIT*len(data))
scaler = fitScaler(data[:train_index+WINDOW_SIZE,1:])
data_norm = normalize_data(data[:,1:],scaler)
print('data_norm shape')
print(data_norm.shape)

dwt_data_train_x_all = []
dwt_data_train_y_all = []
dwt_data_test_x_all = []
dwt_data_test_y_all = []
	
for index in tqdm.tqdm(range(len(data_norm)-WINDOW_SIZE-1)):
	cur_dwt = []
	for col in range(len(data_norm[0])):
		data_col = data_norm[index:index+WINDOW_SIZE,col]
		cA, cD = pywt.dwt(data_col,'db1')
		dwt_col = np.concatenate((cA,cD),axis=-1)

		cur_dwt.extend(dwt_col.tolist())

	if index<train_index:
		dwt_data_train_x_all.append(cur_dwt)
		dwt_data_train_y_all.append(data_norm[index+WINDOW_SIZE+1,:].tolist())
	else:
		dwt_data_test_x_all.append(cur_dwt)
		dwt_data_test_y_all.append(data_norm[index+WINDOW_SIZE+1,:].tolist())

 

with open('dwt_data_hourly_train_x_all_full.csv','w') as f:
	json.dump(dwt_data_train_x_all,f,indent=4)

with open('dwt_data_hourly_train_y_all_full.csv','w') as f:
	json.dump(dwt_data_train_y_all,f,indent=4)

with open('dwt_data_hourly_test_x_all_full.csv','w') as f:
	json.dump(dwt_data_test_x_all,f,indent=4)

with open('dwt_data_hourly_test_y_all_full.csv','w') as f:
	json.dump(dwt_data_test_y_all,f,indent=4)
