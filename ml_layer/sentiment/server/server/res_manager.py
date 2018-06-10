from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from django.apps import AppConfig

import os
import numpy as np
import json
import re
from enum import Enum
import tensorflow as tf
from tensorflow.contrib import learn

class EmailClasses(Enum):
	recall = 0
	status = 1

	def getNoOfClasses():
		return len(list(EmailClasses))
print(EmailClasses(0))

class Sentiment(AppConfig):



	def __init__(self):
		print("initialising module")

		self.checkpoint_dir = "/home/anson/Desktop/hackathons/crypto/sentiment/runs/1528569664/checkpoints"
		self.allow_soft_placement = True
		self.log_device_placement = False


		checkpoint_file = tf.train.latest_checkpoint(self.checkpoint_dir)
		graph = tf.Graph()
		with graph.as_default():
		    session_conf = tf.ConfigProto(
		      allow_soft_placement=self.allow_soft_placement,
		      log_device_placement=self.log_device_placement)
		    self.sess = tf.Session(config=session_conf)
		    with self.sess.as_default():
		        # Load the saved meta graph and restore variables
		        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
		        saver.restore(self.sess, checkpoint_file)

		        # Get the placeholders from the graph by name
		        self.input_x = graph.get_operation_by_name("input_x").outputs[0]
		        self.scores = graph.get_operation_by_name("output/scores").outputs[0]
		        # input_y = graph.get_operation_by_name("input_y").outputs[0]
		        self.dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

		        # Tensors we want to evaluate
		        self.predictions = graph.get_operation_by_name("output/predictions").outputs[0]

	def ready(self):
		""" Called by Django only once during startup
		"""
		# Initialize the auto reply model(should be launched only once)
		# if not any(x in sys.argv for x in ['makemigrations', 'migrate']):  # HACK: Avoid initialisation while migrate
			#do something

		print("In ready")

	@csrf_exempt
	def getResponse(self, request):
		if request.method == "POST":
			print("request")
			print(request.body)
			print(request.POST)

			reqStr = str(request.body,'utf-8')
			reqStrArr = reqStr.split()
			reqStr = ' '.join(reqStrArr)
			print("reqStr")
			print(reqStr)
			requestBody = json.loads(reqStr)
			print(requestBody)

			if requestBody['message'] is not None:
				query = requestBody['message']


				# Map data into vocabulary
				vocab_path = os.path.join(self.checkpoint_dir, "..", "vocab")
				vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
				x_test = np.array(list(vocab_processor.transform([query])))

				# batch_predictions = self.sess.run(self.predictions, {self.input_x: x_test, self.dropout_keep_prob: 1.0})
				batch_scores = self.sess.run(self.scores, {self.input_x: x_test, self.dropout_keep_prob: 1.0})
			
				# answer = batch_predictions[0]
				scores = batch_scores[0]
				scores = scores-np.min(scores)
				print(scores)
				scores = (scores*scores)/sum(scores*scores)
				print(scores)
				pred = np.argmax(scores)
				score = scores[0] + scores[1]*-1
			else:
				score = 0
				res = "Unable to classify request"

		# return HttpResponse(answer)
		# print(HttpResponse(res,content_type="text/plain",charset="utf-8"))
		# print(HttpResponse(res))
		# print(HttpResponse(res,content_type="text/plain",charset="utf-8").getvalue())
		return HttpResponse(score,content_type="text/plain",charset="utf-8")

	def getTemplate(self,_class, utr):
		template = ""

		if utr is None: 
			template = "No utr found"
		else:
			m = re.match(r'SBI', str(utr))
			print("utr")
			print(utr)
			print("m")
			print(m)
			if m is None:
				if _class == 1:
					template = """
Dear Sir,\\n\\n

The status of your inward transaction is as follows:\\n
1. UTR No. =>XXXXXxxxxxxxxxxx\\n
2. Date =>15-03-2017\\n
3. Amount =>1234.00\\n
4. Sending IFSC =>XXXXX0176600\\n
5. Remitter A/c =>1111111111116452\\n
6. Remitter Name =>E456946\\n
7. Remitter Details =>ABC Cop DC Nagar\\n\\n\\n

Regards."""
				else:
					template = """
Dear Sir,\\n\\n

The amount credited to the account xxxxxx mentioned in the mail trail has been remitted back to the remitter account as requested.\\n

The details of the inward transaction are as follows:\\n
1. UTR No. =>XXXXXxxxxxxxxxxx\\n
2. Date =>15-03-2017\\n
3. Amount =>1234.00\\n
4. Sending IFSC =>XXXXX0176600\\n
5. Remitter A/c =>1111111111116452\\n
6. Remitter Name =>E456946\\n
7. Remitter Details =>ABC Cop DC Nagar\\n\\n

Regards."""
			else:
				if _class == 1:
					template = """
Dear Sir,\\n\\n

The status of your outward transaction is as follows:\\n
1. UTR No. =>XXXXXxxxxxxxxxxx\\n
2. Date =>15-03-2017\\n
3. Amount =>1234.00\\n
4. Receiving IFSC =>XXXXX0176600\\n
5. Beneficiary A/c =>1111111111116452\\n
6. Beneficiary Name =>E456946\\n
7. Beneficiary Details =>ABC Cop DC Nagar\\n\\n

Regards."""
				else:
					template = """
Dear Sir,\\n\\n

The transaction to the account mentioned in the mail trail has been recalled.\\n

The details of the outward transaction are as follows:\\n
1. UTR No. =>XXXXXxxxxxxxxxxx\\n
2. Date =>15-03-2017\\n
3. Amount =>1234.00\\n
4. Receiving IFSC =>XXXXX0176600\\n
5. Beneficiary A/c =>1111111111116452\\n
6. Beneficiary Name =>E456946\\n
7. Beneficiary Details =>ABC Cop DC Nagar\\n\\n

Regards."""

		return template


	def saveLog(self, query, _class):
		logFileQ= "server/Log/query.txt"
		logFileL = "server/Log/labels.txt"

		try:
			with open(logFileQ,"a") as f:
				f.write(query+"\n") 			
		except Exception as e:
			raise e


		try:
			with open(logFileL,"a") as f:
				# noOfClasses = EmailClasses.getNoOfClasses()
				f.write(EmailClasses(_class).name+"\n") 			
		except Exception as e:
			raise e

	@csrf_exempt
	def log(self, request):
		if request.method == "POST":
			print("request")
			print(request.body)

			#Java sends string encoded in this format
			reqStr = str(request.body,'ISO 8859-1')
			print("reqStr ISO")
			print(reqStr)
			# reqStr.replace(u'\xa0', u' ').encode('utf-8')
			# reqStr = str(request.body,'utf-8')
			reqStrArr = reqStr.split()
			reqStr = ' '.join(reqStrArr)
			print("reqStr")
			print(reqStr)
			requestBody = json.loads(reqStr)
			print(requestBody)

			logFile= "server/Log/log.txt"

			try:
				with open(logFile,"a") as f:
					f.write(reqStr+"\n") 			
			except Exception as e:
				raise e

			return HttpResponse("Success")





