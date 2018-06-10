import dateutil.parser as dp
import datetime
import requests
import math
import json
import tqdm
import numpy as np
import os
import dateutil.parser as dp

import tensorflow as tf
from keras.models import Sequential
from keras.models import Model, load_model
from keras.layers import Dense
import json
import math
from sklearn.preprocessing import MinMaxScaler
from keras import backend as K
import keras.losses
import keras

import pywt
import time
import pandas as pd

WINDOW_SIZE = 24*10
# model_path = '../models/model_all_square_working.h5'
model_path = '../models/model_all_full.h5'

MAX_NUM_SLOTS = 30
TIME_ZONE = '+05:30'

gdaxBaseUrl = 'https://api.gdax.com/products/{}/candles?start={}&end={}&granularity={}'
cmcBaseUrl = 'https://coinmarketcap.com/currencies/bitcoin/historical-data/?'
if not os.path.exists('exchange_rates'):
	os.makedirs('exchange_rates')
out_file = 'exchange_rates/{}.csv'

def convertToTimestamp(isoFormat):
	parsed_time = dp.parse(isoFormat)
	return int(parsed_time.strftime('%s'))

def convertTimeToMidnight(timestamp):
	d = datetime.datetime.fromtimestamp(timestamp)
	diff = d.hour*3600 + d.minute*60 + d.second
	return timestamp-diff

def convertToIso(timestamp):
	time_obj = datetime.datetime.fromtimestamp(timestamp)
	return time_obj.isoformat()

def convertIsoToStandardDate(date):
	return datetime.datetime.fromtimestamp(int(date)).strftime('%Y%m%d')

def getHistoricalDataFromGdax(product, start, end, granularity):
	data = []

	start_timestamp = convertToTimestamp(start)
	end_timestamp = convertToTimestamp(end)

	num_data = (end_timestamp-start_timestamp)/granularity
	# print(num_data)
	num_slots = math.ceil(num_data/MAX_NUM_SLOTS)
	# print(num_slots)

	print("Started Retrieving Data from APIs")

	for index in range(num_slots):
		cur_start = convertToIso(start_timestamp + index*granularity*MAX_NUM_SLOTS)
		cur_end = convertToIso(min(start_timestamp + (index+1)*granularity*MAX_NUM_SLOTS, end_timestamp))
		# print(cur_start,cur_end)

		url = gdaxBaseUrl.format(product,cur_start,cur_end,granularity)
		#print(url)
		response = requests.get(url)
		if response.status_code == 200:
			s = json.loads(response.content.decode())
			#print(len(s))
			previousDate = 0
			for row in s[::-1]:
				currentDate = convertIsoToStandardDate(row[0])
				print(currentDate)
				if currentDate != previousDate:
					cur_cap = getMcapFromCoinMarketCap(currentDate)
					if cur_cap is not None:
						volume = cur_cap
				# row[0] = convertToIso(row[0] - 19800)
				del row[0]
				row.append(volume)
				# print(len(row))
				data.append(row)
				previousDate = currentDate
		else:
			pass	
		# print("Current End : " + cur_end)
		# print("End : " + end)
		if cur_end >= end:
			print("Finished Retrieving Data from APIs")
			return data;
	return data

def getMcapFromCoinMarketCap(currentDate):
	try:
		# get market info for bitcoin from the start of 2016 to the current day
		bitcoin_market_info = pd.read_html(cmcBaseUrl + 'start=' + currentDate + '&end=' + currentDate)[0]
		# convert the date string to the correct date format
		print('bitcoin market info')
		print(bitcoin_market_info['Date'])
		bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
		# when Volume is equal to '-' convert it to 0
		# print('-----------------------------------')
		# print(bitcoin_market_info['Market Cap'].values=='-')
		#TODO
		if bitcoin_market_info['Market Cap'].values=='-':
			bitcoin_market_info.loc[bitcoin_market_info['Market Cap'].values=='-','Market Cap']=0
		# if bitcoin_market_info['Market Cap'].isnull():
		# 	bitcoin_market_info.loc[bitcoin_market_info['Market Cap'].isnull(),'Market Cap']=0
		# convert to int
		bitcoin_market_info['Market Cap'] = bitcoin_market_info['Market Cap'].astype('int64')
		# look at the first row
		# print(bitcoin_market_info.shape[0])
		return bitcoin_market_info['Market Cap']
	except ValueError:
		print('======================Value error from market cap api===================')
		return None
cur_time = time.time()-10*60*60
start = convertToIso(cur_time-10*24*60*60-10*60*60)
end = convertToIso(cur_time)
granularity = 3600

#TODO: get in ist 00:00 from the api
print('Getting BTC exchange rates...')
rates_btc = getHistoricalDataFromGdax('BTC-USD',start,end,granularity)


# np.savetxt(out_file.format('bitcoin'),rates_btc,delimiter=',',header='time, low, high, open, close, volume')
# np.savetxt(out_file.format('etherium'),rates_btc,delimiter=',',header='time, low, high, open, close, volume')

#make prediction
def fitScaler(data):
    scaler = MinMaxScaler()
    scaler.fit(data)
    return scaler

def normailize_data(data, scaler):
    new_data = scaler.transform(data)
    return new_data

def custom_objective(y_true, y_pred):
    alpha = 100
    loss = K.switch(K.less(y_true*y_pred,0),\
    alpha*y_pred**2-K.sign(y_true)*y_pred+K.abs(y_true),\
    K.square(y_true-y_pred))
    return K.mean(loss,axis=1)

keras.losses.custom_objective = custom_objective

# print(rates_btc)
rates_btc = np.array(rates_btc)
#read the data
rates = rates_btc[:,:]
# print('data_x shape')
# print(data_x.shape)

#get the scaler
df_data = pd.read_csv('../data/bitcoin_historical_hourly_data.csv',sep=',')
data = df_data.as_matrix()
print('data shape')
print(data.shape)
TRAIN_TEST_SPLIT = 0.8
train_index = math.floor(TRAIN_TEST_SPLIT*len(data))
scaler = fitScaler(data[:train_index+WINDOW_SIZE,1:])

# create model
model = load_model(model_path)

def makeDwtFeatures(rates_window):
	dwt = []
	for col in range(len(rates_window[0])):
		data_col = rates_window[:,col]
		cA, cD = pywt.dwt(data_col,'db1')
		dwt_col = np.concatenate((cA,cD),axis=-1)

		dwt.extend(dwt_col.tolist())

	return dwt

rates_norm = scaler.transform(rates)
all_rates = rates_norm.copy()
num_predictions = 24*7
preds_arr = []
timestamp_arr = []
for index in range(num_predictions):
	print('shape of rates')
	print(rates.shape)
	start_index = rates_norm.shape[0]%240
	dwt = makeDwtFeatures(rates_norm[start_index:])
	# print('dwt.shape')
	# print(dwt.shape)
	# Use the model for predictions
	preds = model.predict(np.array([dwt]))[0]
	# preds = [cur_time+index*60*60] + preds
	preds_arr.append(preds)
	# print(preds)
	all_rates = np.concatenate((all_rates,[preds]),axis=0)
	print('all rates shape')
	print(all_rates.shape)
	rates_norm = all_rates[index+1:,:]
	timestamp_arr.append(cur_time+60*60*index)

timestamp_arr = np.expand_dims(timestamp_arr,axis=1)
# print(timestamp_arr)
preds_arr_denormalised = scaler.inverse_transform(preds_arr)
preds_arr_denormalised = np.concatenate((timestamp_arr,preds_arr_denormalised),axis=-1)

arr_to_write = []
for el in preds_arr_denormalised:
	tmp = []
	tmp.append(datetime.datetime.fromtimestamp(el[0]).strftime('%Y-%m-%d %H:%M:%S'))
	for el_1 in el[1:]:
		tmp.append(el_1)
	arr_to_write.append(tmp)
# print(len(preds_arr))
df_preds = pd.DataFrame(arr_to_write)
df_preds.to_csv('predictions.csv',sep=',',header=['timestamp','low(USD)','high(USD)','open(USD)','close(USD)','volume(USD)','market_cap'],index=0)
# np.savetxt('predictions.csv',preds_arr_denormalised,delimiter=',',header='timestamp,low,high,open,close,volume,market_cap')