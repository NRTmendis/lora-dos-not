# Author Nissanka Mendis. LSTM Multivariate localisation algorithm and training 2018 Feb.
# Based on code by Jason Brownlee
# At https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

from math import sqrt
from numpy import concatenate
from numpy import array
from matplotlib import pyplot
from pandas import read_csv
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout, MaxPooling2D, BatchNormalization
from keras.layers import LSTM
from time import strftime
import sys
sys.path.insert(1, '..')
from utils import get_current_world, get_current_model, get_gateways

# SETTINGS CONSTANTS
CURRENT_WORLD = get_current_world()
CURRENT_MODEL = get_current_model()


def train_localisation_model(epCH=500, CSV_file='lora_GTW_PP.csv'):
    current_time = strftime("%d%m%y_%H%M%S")
    # load dataset
    dataset = read_csv(CSV_file, header=0, index_col=0)
    values = dataset.values
    # ensure all data is float
    values = values.astype('float32')
    # normalize features
    scaler = StandardScaler()
    scaler.fit(values)
    scaled = scaler.fit_transform(values)
    joblib.dump(scaler, "{}_{}{}".format(CURRENT_WORLD,
                                         current_time, ".save"))
    # split into train and test sets
    train = scaled
    # split into input and outputs
    train_X, train_y = train[:, :-2], train[:, -2:]
    # reshape input to be 3D [samples, steps, features]
    train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
    # design network
    model = Sequential()
    model.add(LSTM(500, activation='relu', input_shape=(
        train_X.shape[1], train_X.shape[2])))
    print(train_X.shape[1], train_X.shape[2])
    model.add(Dropout(0.3))
    # model.add(MaxPooling2D((10, 10)))
    # model.add(Dropout(0.3))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='mean_squared_error',
                  optimizer='adam', metrics=['accuracy'])
    # fit network
    model.fit(train_X, train_y, epochs=epCH,
              batch_size=72, verbose=1, shuffle=True)
    # save model
    model.save("{}_{}{}".format(CURRENT_WORLD,
                                current_time, ".h5"))


def loc_single_predict(test_Val, QUERY_CSV_BATCH='none.csv'):
    if QUERY_CSV_BATCH != 'none.csv':
        # run batch in CSVinstead of value
        dataset_Q = read_csv(QUERY_CSV_BATCH, header=0, index_col=0)
        values_Q = dataset_Q.values
        test_Vals = values_Q.astype('float32')
    else:
        # combine test value and dataset used to train model
        for row in test_Val:
            del row[0]  # Remove ID from array.
        test_Val = array(test_Val)
        test_Vals = test_Val.astype('float32')
    # normalize features
    scaler = joblib.load('{}.save'.format(CURRENT_MODEL))
    scaled = scaler.transform(test_Vals)
    # split back to test value
    check = scaled[-int(test_Vals.shape[0]):, :]
    # split into input and outputs
    test_X, test_y = check[:, :-2], check[:, -2:]
    # reshape input to be 3D [samples, steps, features]
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    # load exisiting model
    model = load_model('{}.h5'.format(CURRENT_MODEL))
    # make a prediction
    yhat = model.predict(test_X)
    test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
    # invert scaling for forecast
    inv_yhat = concatenate((test_X, yhat), axis=1)
    inv_yhat = concatenate((scaled, inv_yhat), axis=0)
    inv_yhat = scaler.inverse_transform(inv_yhat)
    inv_yhat = inv_yhat[-int(test_Vals.shape[0]):, -2:]
    return (inv_yhat.tolist())
