import requests
import datetime
import time
import math
import json
import tqdm
import os
import dateutil.parser as dp
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

import pdb

# pdb.set_trace()

MAX_NUM_SLOTS = 30
TIME_ZONE = '+05:30'

gdaxBaseUrl = 'https://api.gdax.com/products/{}/candles?start={}&end={}&granularity={}'
product = 'BTC-USD'
start = '2017-06-01T00:00:00'
end = '2018-06-01T00:00:00'
granularity = 900

cmcBaseUrl = 'https://coinmarketcap.com/currencies/bitcoin/historical-data/?'


if not os.path.exists('historical_data'):
	os.makedirs('historical_data')
out_file = 'historical_data/{}.csv'

def convertToTimestamp(isoFormat):
	currentTime = dp.parse(isoFormat)
	#return int(currentTime.strftime('%s'))
	return int(time.mktime(currentTime.timetuple()))

def convertTimeToMidnight(timestamp):
	d = datetime.datetime.fromtimestamp(timestamp)
	diff = d.hour*3600 + d.minute*60 + d.second
	return timestamp-diff

def convertToIso(timestamp):
	return datetime.datetime.fromtimestamp(timestamp).isoformat()

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
					volume = getMcapFromCoinMarketCap(currentDate)
				row[0] = convertToIso(row[0] - 19800)
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
	# get market info for bitcoin from the start of 2016 to the current day
	bitcoin_market_info = pd.read_html(cmcBaseUrl + 'start=' + currentDate + '&end=' + currentDate)[0]
	# convert the date string to the correct date format
	bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
	# when Volume is equal to '-' convert it to 0
	# print('-----------------------------------')
	# print(bitcoin_market_info['Market Cap'].values)
	if bitcoin_market_info['Market Cap'].values[0]=='-' or bitcoin_market_info['Market Cap'].values[0]==None:
		return 0
	return bitcoin_market_info['Market Cap'].values[0]


#TODO: get in ist 00:00 from the api
print('Getting BTC historical data...')
btc_price = getHistoricalDataFromGdax(product,start,end,granularity)
# print(rates_btc[0:10])
# print(type(rates_btc))

df=pd.DataFrame(btc_price)
df.to_csv(out_file.format('bitcoin_historical_quarterhourly_data'), mode='w', sep=',', header=['time', 'low', 'high', 'open', 'close', 'volume', 'market cap'], index=0)