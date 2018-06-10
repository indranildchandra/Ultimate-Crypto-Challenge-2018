import requests
import dateutil.parser as dp
import numpy as np
import json
import tqdm
import time
import datetime
import math

baseUrl = 'https://api.gdax.com/products/{}/candles?start={}&end={}&granularity={}'
MAX_NUM_SLOTS = 30

def convertToTimestamp(isoFormat):
	parsed_time = dp.parse(isoFormat)
	return int(parsed_time.strftime('%s'))

def getSentiment(tweet):
	res = requests.post('http://localhost:8000/message/',json={'message': tweet},headers={'Content-Type': 'Application/json'})
	# print(res)
	if res.status_code == 200:
		content = float(res.content.decode())
		# print('content')
		# print(content)
		return content
	else:
		return 0

def convertToTimestamp(isoFormat):
	parsed_time = dp.parse(isoFormat)
	return int(parsed_time.strftime('%s'))

def convertToIso(timestamp):
	time_obj = datetime.datetime.fromtimestamp(timestamp)
	return time_obj.isoformat()

def getHistoricExchangeRates(product, start, end, granularity):
	data = []

	start_timestamp = convertToTimestamp(start)
	end_timestamp = convertToTimestamp(end)

	num_data = (end_timestamp-start_timestamp)/granularity
	num_slots = math.ceil(num_data/MAX_NUM_SLOTS)

	for index in range(num_slots):
		cur_start = convertToIso(start_timestamp + index*granularity*MAX_NUM_SLOTS)
		cur_end = convertToIso(min(start_timestamp + (index+1)*granularity*MAX_NUM_SLOTS, end_timestamp))
		
		url = baseUrl.format(product,cur_start,cur_end,granularity)
		# print(url)
		response = requests.get(url)
		if response.status_code == 200:
			s = json.loads(response.content.decode())
			# print(len(s))
			data.extend(s)
		else:
			pass

	# print(len(data))
	return data

twitter_api_url = 'http://192.168.43.249:3000/crypto/trends?keyword=%20bitcoin%20price'

res = requests.get(twitter_api_url)

print(res.content)

gip_data = []

content = None

if res.status_code != 200:
	with open('twitter_Sample.json', 'r') as f:
		content = json.load(f)
elif res.status_code == 200:
	content = json.loads(res.content.decode())

if content:
	for popular_tweet in tqdm.tqdm(content):
		rank = popular_tweet['rank']
		eng_score = popular_tweet['engagement_score']
		count = popular_tweet['trend_factor']

		cur_gip = eng_score**2 + (1/rank)**2 + count**2

		for tweet in popular_tweet['user_tweets']:
			cur_sentiment = getSentiment(tweet['tweet_content'])
			timestamp = convertToTimestamp(tweet['tweet_date'])
			gip_data.append([timestamp, cur_gip, cur_sentiment])

	gip_data = np.array(gip_data)
	sorted_indices = np.argsort(gip_data[:,0])
	print('sorted indices')
	print(sorted_indices)
	gip_data = gip_data[sorted_indices,:]

	rate_arr = []
	for data in tqdm.tqdm(gip_data):
		start = convertToIso(data[0])
		end = convertToIso(data[0]+60)
		rate = getHistoricExchangeRates('BTC-USD',start,end,60)[0]
		rate_arr.append(rate)
		# data.extend(rate) 
	rate_arr = np.array(rate_arr)
	gip_data = np.concatenate((gip_data,rate_arr),axis=-1)

	np.savetxt('gip.csv',gip_data,delimiter=',',header='timestamp,gip,sentiment,low,high,open,close,volume')

