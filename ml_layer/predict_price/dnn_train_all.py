import pandas as pd
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint
from keras.callbacks import Callback
from keras.layers import Activation, Dropout
import json
from keras import backend as K
import keras.losses
import keras

np.random.seed(42)

saveEveryBatch = 100
model_path = '../models/model_all_full.h5'
restore = False

class WeightsSaver(Callback):
    def __init__(self, model, N):
        self.model = model
        self.N = N
        self.batch = 0

    def on_batch_end(self, batch, logs={}):
        if self.batch % self.N == 0:
            # name = 'model.h5' % self.batch
            self.model.save(model_path,overwrite=True)
        self.batch += 1

def custom_objective(y_true, y_pred):
	alpha = 100
	loss = K.switch(K.less(y_true*y_pred,0),\
	alpha*y_pred**2-K.sign(y_true)*y_pred+K.abs(y_true),\
	K.square(y_true-y_pred))
	# loss = K.square(y_true-y_pred)
	
	# return K.mean(K.mean(loss,axis=-1),axis=-1)
	return K.mean(loss,axis=-1)

keras.losses.custom_objective = custom_objective

#read the data
with open('../data/dwt_data_hourly_train_x_all_full.csv','r') as f:
	data_x = json.load(f)
	data_x = np.array(data_x)
with open('../data/dwt_data_hourly_train_y_all_full.csv','r') as f:
	data_y = json.load(f)
	data_y = np.array(data_y)

if restore == True:
	model = keras.models.load_model(model_path)
else:
	# create model
	TRAIN_SIZE = data_x.shape[1]
	model = Sequential()
	model.add(Dense(500, input_shape=(TRAIN_SIZE,)))
	model.add(Activation('relu'))
	model.add(Dropout(0.25))
	model.add(Dense(250))
	model.add(Activation('relu'))
	model.add(Dense(6, use_bias=True))
	model.add(Activation('linear'))

model.compile(optimizer='adam', loss=custom_objective)

# Fit the model
model.fit(data_x, data_y, epochs=150, batch_size=10, callbacks=[WeightsSaver(model,saveEveryBatch)])