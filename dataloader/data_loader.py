import pandas as pd
import yfinance as yf

from yahoo_fin import stock_info as sf
from utils.utils import check_market, make_ticker_nse

class Dataloader:

    def __init__(self, index:str, start_date:str, end_date:str) -> None:
        self._index = index
        self._start_date = start_date
        self._end_date = end_date

        # Index Name Dictionary
        self._index_dictionary = {'NIFTY_50':('^NSEI', 'sf.tickers_nifty50()'), 'NIFTY_BANK':('^NSEBANK', 'sf.tickers_niftybank()'),
                                  'NASDAQ':('^IXIC', 'sf.tickers_nasdaq()'), 'SP500':('^GSPC', 'sf.tickers_sp500()'), 'FTSE250':('^FTMC', 'sf.tickers_ftse250()'),
                                  'FTSE100':('^FTSE', 'sf.tickers_ftse100()'), 'DOW':('^DJI', 'sf.tickers_dow()'), 'IBOVESPA':('^BVSP', 'sf.tickers_ibovespa()'),
                                  'NSE':('^NSEI', 'None')}

    def load_data(self) -> None:
        self._all_data = pd.DataFrame()
        for equity in self._tickers:
            if equity != "MM.NS":
                data = yf.download(equity, start=self._start_date, end=self._end_date, progress=False, show_errors=False)
                data['TIC'] = equity
                self._all_data = self._all_data.append(data)

    def load_baseline(self) -> None:
        # loading the baseline data
        self._baseline = yf.download(tickers=self._index_dictionary[self.getIndex()][0], start=self._start_date, end=self._end_date, progress=False)

    def load_all_index_tickers(self) -> None:
        # load all tickers inside a given index
        if eval(self._index_dictionary[self.getIndex()][1]) != None and check_market(self._index):
            self._tickers = make_ticker_nse(eval(self._index_dictionary[self.getIndex()][1]))
        elif eval(self._index_dictionary[self.getIndex()][1]) == None and check_market(self._index):
            self._tickers = make_ticker_nse(make_ticker_nse(pd.read_csv('datastore/NSE550.csv')['Symbol'].to_list()))
        else:
            self._tickers = eval(self._index_dictionary[self.getIndex()][1])

    def getIndex(self) -> None:
        return self._index

    def getIndexData(self) -> pd.DataFrame:
        return self._baseline

    def resampler(self, df:pd.DataFrame=pd.DataFrame(), dataType:str="baseline", frequency:str="M") -> pd.DataFrame:
        if dataType == "securities":
            return self.resample_df(df, frequency=frequency)
        elif dataType == "baseline":
            return self._baseline.resample(frequency).last().dropna()

    def resample_df(self, _data, frequency) -> pd.DataFrame:
        return _data.resample(frequency).last().dropna()

    def getAllindextickers(self) -> list:
        return self._tickers

    def getAllindexdata(self) -> pd.DataFrame:
        return self._all_data
