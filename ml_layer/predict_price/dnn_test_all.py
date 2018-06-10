import pandas as pd
import numpy as np
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

import matplotlib.pyplot as plt

np.random.seed(42)

saveEveryBatch = 100
WINDOW_SIZE = 24*10
model_path = '../models/BTC_price_predictor_model.h5'

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

#read the data
with open('../data_processing_layer/output/dwt_data_hourly_test_x_all.csv','r') as f:
	data_x = json.load(f)
	data_x = np.array(data_x)
with open('../data_processing_layer/output/dwt_data_hourly_test_y_all.csv','r') as f:
	data_y = json.load(f)
	data_y = np.array(data_y)

#get the scaler
df_data = pd.read_csv('../data_processing_layer/input_data/train.csv',sep=',')
data = df_data.as_matrix()
print('data shape')
print(data.shape)
TRAIN_TEST_SPLIT = 0.8
train_index = math.floor(TRAIN_TEST_SPLIT*len(data))
scaler = fitScaler(data[:train_index+WINDOW_SIZE,1:])

# create model
model = load_model(model_path)

# Use the model for predictions
preds = model.predict(data_x)

# denormalized_preds = preds*(scaler.data_max_[2] - scaler.data_min_[2]) + scaler.data_min_[2]
# preds_ex = np.expand_dims(preds,axis=-1)
# preds_conc = np.concatenate((preds,preds,preds,preds,preds,preds),axis=-1)
# denormalized_preds = scaler.inverse_transform(preds_conc)[:,2]

denormalized_preds = scaler.inverse_transform(preds)
# print(denormalized_preds)
# print(len(denormalized_preds))

df_data = pd.read_csv('../data_processing_layer/input_data/train.csv',sep=',')
data_original = df_data.as_matrix()
# print('data_original shape')
# print(data_original.shape)
data_test = data_original[train_index+WINDOW_SIZE+1:,1:]

# denormalized_preds = denormalized_preds + (data_test[0,:]-denormalized_preds[0,:])
# denormalized_preds = denormalized_preds + 2*(data_test[0,2]-denormalized_preds)


# print(len(opening_price))

plt.title('low')
plt.subplot(3,2,1).plot(data_test[:,0],color="blue")
plt.subplot(3,2,1).plot(denormalized_preds[:,0],color="red")
plt.title('low')

plt.subplot(3,2,2).plot(data_test[:,1],color="blue")
plt.subplot(3,2,2).plot(denormalized_preds[:,1],color="red")
plt.title('high')

plt.subplot(3,2,3).plot(data_test[:,2],color="blue")
plt.subplot(3,2,3).plot(denormalized_preds[:,2],color="red")
plt.title('open')

plt.subplot(3,2,4).plot(denormalized_preds[:,3],color="red")
plt.subplot(3,2,4).plot(data_test[:,3],color="blue")
plt.title('close')

plt.subplot(3,2,5).plot(data_test[:,4],color="blue")
plt.subplot(3,2,5).plot(denormalized_preds[:,4],color="red")
plt.title('volume')

plt.subplot(3,2,6).plot(data_test[:,5],color="blue")
plt.subplot(3,2,6).plot(denormalized_preds[:,5],color="red")
plt.title('market cap')



plt.tight_layout()
plt.show()

df = pd.DataFrame(denormalized_preds)
df.to_csv('../output/data/BTC_price_prediction_may.csv',sep=',',index=0,header=None)