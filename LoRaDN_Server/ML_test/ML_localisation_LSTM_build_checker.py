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
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
 
# load dataset
dataset = read_csv('lora_GTW_PP.csv', header=0, index_col=0)
values = dataset.values
# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = StandardScaler()
scaled = scaler.fit_transform(values)
#joblib.dump(scaler, 'scaler.save') 

# split into train and test sets
#values = reframed.values
values = scaled
n_train_pkts = int(len(values)*0.1)
train = values[:n_train_pkts, :]
test = values[n_train_pkts:, :]
# split into input and outputs
train_X, train_y = train[:, :-2], train[:,-2:]
test_X, test_y = test[:, :-2], test[:,-2:]
# reshape input to be 3D [samples, steps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

# design network
#model = Sequential()
#model.add(LSTM(1000, input_shape=(train_X.shape[1], train_X.shape[2])))
#model.add(Dense(2))
#model.compile(loss='mean_squared_error', optimizer='adam')
# fit network
#history = model.fit(train_X, train_y, epochs=1000, batch_size=72, validation_data=(test_X, test_y), verbose=1, shuffle=True)
#model.save('localisation_model.h5')

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
rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
print('Test RMSE: %.3f' % rmse)

# plot history
#pyplot.plot(history.history['loss'], label='train')
#pyplot.plot(history.history['val_loss'], label='test')
#pyplot.legend()
#pyplot.show()
