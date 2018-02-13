#Author Nissanka Mendis. LSTM Multivariate localisation algorithm and training 2018 Feb.
#Based on code by Jason Brownlee 
#At https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

from math import sqrt
from numpy import concatenate
from numpy import array
from matplotlib import pyplot
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.externals import joblib
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
 
def train_localisation_model(epCH=500,CSV_file='lora_GTW_PP.csv'):
	# load dataset
	dataset = read_csv(CSV_file, header=0, index_col=0)
	values = dataset.values
	# ensure all data is float
	values = values.astype('float32')
	# normalize features
	scaler = MinMaxScaler(feature_range=(0, 1))
	scaled = scaler.fit_transform(values)
	# split into train and test sets
	train = scaled
	# split into input and outputs
	train_X, train_y = train[:, :-2], train[:,-2:]
	# reshape input to be 3D [samples, steps, features]
	train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
	# design network
	model = Sequential()
	model.add(LSTM(epCH, input_shape=(train_X.shape[1], train_X.shape[2])))
	model.add(Dense(2))
	model.compile(loss='mean_squared_error', optimizer='adam')
	# fit network
	model.fit(train_X, train_y, epochs=epCH, batch_size=72, verbose=1, shuffle=True)
	# save model
	model.save('localisation_model.h5')

def loc_single_predict(test_Val, QUERY_CSV_BATCH='none.csv', GTW_CSV_file='lora_GTW_PP.csv'):
	# load dataset
	dataset = read_csv(GTW_CSV_file, header=0, index_col=0)
	values = dataset.values
	# ensure all data is float
	values = values.astype('float32')
	if QUERY_CSV_BATCH != 'none.csv':
		#run batch in CSVinstead of value
		dataset_Q = read_csv(QUERY_CSV_BATCH, header=0, index_col=0)
		values_Q = dataset_Q.values
		test_Vals = values_Q.astype('float32')
		values = concatenate((values,test_Vals), axis=0)
	else:
		# combine test value and dataset used to train model
		for row in test_Val:
			del row[0] #Remove ID from array.
		test_Val = array(test_Val)
		test_Vals = test_Val.astype('float32')
		values = concatenate((values,test_Vals), axis=0)
	# normalize features
	scaler = MinMaxScaler(feature_range=(0, 1))
	scaled = scaler.fit_transform(values)
	# split back to test value
	check = scaled[-int(test_Vals.shape[0]):,:]
	# split into input and outputs
	test_X, test_y = check[:, :-2], check[:,-2:]
	# reshape input to be 3D [samples, steps, features]
	test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
	# load exisiting model
	model = load_model('localisation_model.h5')
	# make a prediction
	yhat = model.predict(test_X)
	test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
	# invert scaling for forecast
	inv_yhat = concatenate((test_X, yhat), axis=1)
	inv_yhat = concatenate((scaled,inv_yhat), axis=0)
	inv_yhat = scaler.inverse_transform(inv_yhat)
	inv_yhat = inv_yhat[-int(test_Vals.shape[0]):,-2:]
	return (inv_yhat.tolist())