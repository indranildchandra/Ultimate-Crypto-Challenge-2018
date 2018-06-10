from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse, JsonResponse

import numpy as np
import time
import datetime
import dateutil.parser as dp
import math
import pandas as pd

MAX_NUM_SLOTS = 30

# Create your views here.
class Api():

	def __init__(self):
		self.baseUrl = 'https://api.gdax.com/products/{}/candles?start={}&end={}&granularity={}'
		self.twitter_api_url = 'http://192.168.43.249:3000/crypto/trends?keyword=%20bitcoin%20price'
		

	@csrf_exempt
	def getInfluencers(self, request):
		twitterData = self.getTwitterData()
		popularInfluencerData = []
		name = {}
		count = 0
		for data in twitterData:
			if count>=5:
				break
			if name.get(data['user_name'],-1) == -1:
				name[data['user_name']]=1
				popularInfluencerData.append({
					'name': data['user_name'],
					'twitter_handle': data['twitter_handle']
				})
				count += 1
		return JsonResponse(popularInfluencerData,safe=False)

	@csrf_exempt 
	def getPopularTweets(self, request):
		twitterData = self.getTwitterData()
		popularTweetData = []
		name = {}
		count = 0
		for data in twitterData:
			if count>=5:
				break
			popularTweetData.append({
				'popular_tweet_content': data['popular_tweet_content'],
				'twitter_handle': data['twitter_handle'],
				'likes': data['likes_count'],
				'retweet': data['retweet_count'],
				'name': data['user_name']
			})
			count += 1
		return JsonResponse(popularTweetData,safe=False)

	def convertToTimestamp(self,isoFormat):
		currentTime = dp.parse(isoFormat)
		#return int(currentTime.strftime('%s'))
		return int(time.mktime(currentTime.timetuple()))

	def convertTimeToMidnight(self,timestamp):
		d = datetime.datetime.fromtimestamp(timestamp)
		diff = d.hour*3600 + d.minute*60 + d.second
		return timestamp-diff

	def formatTimestamp(self,timestamp):
		d = datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S')
		return d

	@csrf_exempt
	def getPrice(self, request):
		# product = 'BTC-USD'
		# start = self.convertToIso(time.time()-10*60-60*60)
		# end  = self.convertToIso(time.time()-60*60)
		# print(start,end)
		# granularity = 60
		# rates = self.getHistoricExchangeRates(product,start,end,granularity)

		# rate_arr = []
		# for rate in rates[::-1]:
		# 	rateObj = {
		# 		'timestamp': datetime.datetime.fromtimestamp(rate[0]).strftime('%d/%m %H:%M'),
		# 		'low': rate[1],
		# 		'high': rate[2],
		# 		'open': rate[3],
		# 		'close': rate[4],
		# 		'volume': rate[5]
		# 	}
		# 	rate_arr.append(rateObj)

		df = pd.read_csv('../../data_processing_layer/input_data/train.csv',delimiter=',' )
		# data = np.loadtxt(,)
		data = df.as_matrix()
		# print('data_original shape')
		# print(data_original.shape)
		WINDOW_SIZE = 24*10
		TRAIN_TEST_SPLIT = 0.8
		train_index = math.floor(TRAIN_TEST_SPLIT*len(data))
		# scaler = fitScaler(data[:train_index+WINDOW_SIZE,1:])
		data_test = data[train_index+WINDOW_SIZE+1:,:]
		data_obj_arr_actual = []
		for el in data_test:
			data_obj_arr_actual.append({
				'timestamp': self.formatTimestamp(self.convertToTimestamp(el[0])),
				'actual_low': el[1],
				'actual_high': el[2],
				'actual_open': el[3],
				'actual_close': el[4],
				'actual_volume': el[5]
				})

		df = pd.read_csv('../../output/data/BTC_price_prediction_may.csv',delimiter=',' )
		# data = np.loadtxt(,)
		data = df.as_matrix()
		# print(data_test.shape)
		# print(data.shape)
		data_obj_arr_predicted = []
		for index,el in enumerate(data_test):
			if index>=data.shape[0]:
				break
			data_obj_arr_actual[index]['predicted_low'] = data[index][0]
			data_obj_arr_actual[index]['predicted_high'] = data[index][1]
			data_obj_arr_actual[index]['predicted_open'] = data[index][2]
			data_obj_arr_actual[index]['predicted_close'] = data[index][3]

		return JsonResponse(data_obj_arr_actual,safe=False)


	@csrf_exempt
	def getOutputPrice(self, request):
		df = pd.read_csv('../../data_processing_layer/input_data/train.csv',delimiter=',' )
		# data = np.loadtxt(,)
		data = df.as_matrix()
		data_res = data[7291:,:]
		data_obj_arr = []
		for el in data_res:
			data_obj_arr.append({
				'timestamp': el[0],
				'low': el[1],
				'high': el[2],
				'open': el[3],
				'close': el[4],
				'volume': el[5],
				'market_cap': el[6]
				})
		return JsonResponse(data_obj_arr,safe=False)

	def getTwitterData(self):
		try:
			res = requests.get(self.twitter_api_url)

			print(res.content)

			gip_data = []

			content = None

			if res.status_code != 200:
				with open('../twitter_Sample.json', 'r') as f:
					content = json.load(f)
			elif res.status_code == 200:
				content = json.loads(res.content.decode())
		except requests.exceptions.ConnectionError:
			with open('../twitter_Sample.json', 'r') as f:
				content = json.load(f)

		for popular_tweet in content:
			rank = popular_tweet['rank']
			eng_score = popular_tweet['engagement_score']
			count = popular_tweet['trend_factor']

			cur_gip = eng_score + (1/rank) + count

			gip_data.append(cur_gip)

		gip_data = np.array(gip_data)
		sorted_indices = np.argsort(gip_data)[::-1]
		# print('sorted indices')
		# print(sorted_indices)
		sorted_Content = []
		for index in sorted_indices:
			sorted_Content.append(content[index])

		return sorted_Content

	def convertToTimestamp(self, isoFormat):
		parsed_time = dp.parse(isoFormat)
		return int(parsed_time.strftime('%s'))

	def convertToIso(self, timestamp):
		time_obj = datetime.datetime.fromtimestamp(timestamp)
		return time_obj.isoformat()

	def getHistoricExchangeRates(self, product, start, end, granularity):
		data = []

		start_timestamp = self.convertToTimestamp(start)
		end_timestamp = self.convertToTimestamp(end)

		num_data = (end_timestamp-start_timestamp)/granularity
		num_slots = math.ceil(num_data/MAX_NUM_SLOTS)

		for index in range(num_slots):
			cur_start = self.convertToIso(start_timestamp + index*granularity*MAX_NUM_SLOTS)
			cur_end = self.convertToIso(min(start_timestamp + (index+1)*granularity*MAX_NUM_SLOTS, end_timestamp))
			
			url = self.baseUrl.format(product,cur_start,cur_end,granularity)
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

	def getOverallSentiments(self, request):
		tweetData = self.getTwitterData()

		num_positives = 0
		num_negatives = 0

		for tweet in tweetData:
			score = requests.post('http://localhost:8000/message/',json={'message': tweet['popular_tweet_content']})
			score = float(score.content)
			if score>0:
				num_positives += 1
			elif score<0:
				num_negatives += 1

		general_sentiment = 'Positive' if num_negatives<=num_positives else 'Negative'
		score = max(num_positives,num_negatives)/(num_negatives+num_positives)*100
		score = str(score) + '%'
		return JsonResponse({
				'general_sentiment': general_sentiment,
				'score': score
			})

