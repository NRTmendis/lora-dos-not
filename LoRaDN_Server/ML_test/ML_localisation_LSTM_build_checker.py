#Author Nissanka Mendis. LSTM Multivariate localisation algorithm and training 2018 Feb.
#Based on code by Jason Brownlee 
#At https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

Train_Now = True #Train or use model

# load dataset
dataset = read_csv('lora_GTW_PP.csv', header=0, index_col=0)
values = dataset.values
# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = StandardScaler()
scaled = scaler.fit_transform(values)
joblib.dump(scaler, 'scaler.save') 

# split into train and test sets
values = scaled
if Train_Now:
	pkt_ratio = 0.75
else:
	pkt_ratio = 0.1
n_train_pkts = int(len(values)*pkt_ratio)
train = values[:n_train_pkts, :]
test = values[n_train_pkts:, :]
# split into input and outputs
train_X, train_y = train[:, :-2], train[:,-2:]
test_X, test_y = test[:, :-2], test[:,-2:]
# reshape input to be 3D [samples, steps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

if Train_Now:
	# design network
	model = Sequential()
	model.add(LSTM(500, input_shape=(train_X.shape[1], train_X.shape[2])))
	model.add(Dense(2))
	model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['accuracy'])
	# fit network
	history = model.fit(train_X, train_y, epochs=150, batch_size=72, validation_data=(test_X, test_y), verbose=1, shuffle=True)
	model.save('localisation_model.h5')
else:
	model = load_model('localisation_model.h5')
	scaler = joblib.load('scaler.save') 

# make a prediction
yhat = model.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# invert scaling for forecast
inv_yhat = concatenate((test_X, yhat), axis=1)
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:,-2:]
print(inv_yhat)
# invert scaling for actual
test_y = test_y.reshape((len(test_y), 2))
inv_y = concatenate((test_X, test_y), axis=1)
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,-2:]
print(inv_y)
# calculate RMSE
mae = mean_absolute_error(inv_y, inv_yhat)
print('Test MAE: %.3f' % mae)

# plot history
pyplot.plot(history.history['acc'])
pyplot.plot(history.history['val_acc'])
pyplot.title('model accuracy')
pyplot.ylabel('accuracy')
pyplot.xlabel('epoch')
pyplot.legend(['train', 'test'], loc='upper left')
pyplot.show()
# summarize history for loss
pyplot.plot(history.history['loss'])
pyplot.plot(history.history['val_loss'])
pyplot.title('model loss')
pyplot.ylabel('loss')
pyplot.xlabel('epoch')
pyplot.legend(['train', 'test'], loc='upper left')
pyplot.show()
