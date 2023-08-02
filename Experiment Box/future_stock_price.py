import warnings
warnings.filterwarnings("ignore")

import talib as tb
import numpy as np
import pandas as pd

from sklearn.linear_model import Lasso


def predict_month_ahead(ticker:str, future_date:str, TRAIN_START="2008-01-01", TRAIN_END="2017-11-30", TEST_START="2017-12-01", TEST_END="2023-07-31"):

    data = pd.read_csv(f"Data/{ticker}.csv", index_col=0, parse_dates=True)

    data['SMA'] = tb.SMA(data['Adj Close'], timeperiod=10) - tb.SMA(data['Adj Close'], timeperiod=30)
    data['EMA'] = tb.EMA(data['Adj Close'], timeperiod=10) - tb.EMA(data['Adj Close'], timeperiod=30)
    data["RSI"] = tb.RSI(data["Adj Close"], timeperiod=14)

    data.dropna(inplace=True)
    data['Label'] = data['Adj Close'].shift(-21)

    data = data[['Adj Close', 'SMA', 'EMA', 'RSI', 'Label']]
    X_train, y_train, X_test, y_test = data.loc[TRAIN_START:TRAIN_END].drop("Label", axis=1), data["Label"].loc[TRAIN_START:TRAIN_END], data.loc[TEST_START:TEST_END].drop("Label", axis=1), data["Label"].loc[TEST_START:TEST_END]

    model = Lasso(0.25)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    X_test["Predicted Close"] = preds
    X_test["TIC"] = ticker

    return (X_test[["Predicted Close"]].resample("M").last().loc[:future_date].pct_change() * 12).loc[future_date]
