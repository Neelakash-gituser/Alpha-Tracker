import datetime
import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import os
import glob
import pandas as pd
import yfinance as yf
import logging as log

from yahoo_fin import stock_info as sf
from utils.utils import check_market, make_ticker_nse_bse, make_ticker_nse
from logger._logger import logger, get_exception_line_no

log.getLogger('yfinance').setLevel(log.CRITICAL)

logger_data = logger.getLogger("DataLoader")

class Dataloader:

    def __init__(self, index:str, start_date:str, end_date:str) -> None:
        """
        Initialize a Dataloader instance.

        This constructor initializes a Dataloader object with the specified financial index, start date,
        and end date. It also creates an index dictionary for mapping index names to relevant data sources.

        :param index: The financial index associated with the data loader.
        :type index: str

        :param start_date: The start date for retrieving financial data.
        :type start_date: str

        :param end_date: The end date for retrieving financial data.
        :type end_date: str

        :return: None
        """
        self._index = index
        self._start_date = start_date
        self._end_date = end_date

        # Index Name Dictionary
        self._index_dictionary = {'NIFTY_50':('^NSEI', 'sf.tickers_nifty50()'), 'NIFTY_BANK':('^NSEBANK', 'sf.tickers_niftybank()'),
                                  'NASDAQ':('^IXIC', 'sf.tickers_nasdaq()'), 'SP500':('^GSPC', 'sf.tickers_sp500()'), 'FTSE250':('^FTMC', 'sf.tickers_ftse250()'),
                                  'FTSE100':('^FTSE', 'sf.tickers_ftse100()'), 'DOW':('^DJI', 'sf.tickers_dow()'), 'IBOVESPA':('^BVSP', 'sf.tickers_ibovespa()'),
                                  'NSE/BSE':('^NSEI', 'None')}
        
        
    def load_single_instrument(self, stock_name) -> pd.DataFrame:
        """
        Load historical stock price data for a single instrument.

        Args:
            stock_name (str): The ticker symbol or name of the stock instrument to load.

        Returns:
            pd.DataFrame: A Pandas DataFrame containing historical stock price data
                        for the specified instrument, with columns 'Open', 'High',
                        'Low', 'Close', 'Volume', and 'Adj Close'.

        Raises:
            Exception: If there is an issue with downloading the data, an exception
                    is caught, and an error message is logged with details about the
                    problem.

        Note:
            This function uses the Yahoo Finance API (yfinance) to download historical
            stock price data for the specified instrument within the date range defined
            by `start_date` and `end_date`.

        Example:
            To load historical data for Apple Inc. (AAPL) within a specified date range,
            you can call the function like this:

            >>> data = load_single_instrument('AAPL')
        """
        try:
            data = yf.download(stock_name, start=self._start_date, end=self._end_date, progress=False)
            return data
        except Exception as e:
            logger_data.info(f"problem {e} in load_single_instrument() at line no.={get_exception_line_no()}")


    def load_data(self) -> None:
        """
        Load historical stock price data for multiple instruments and store it in a combined DataFrame.

        This method downloads historical stock price data for a list of ticker symbols (equities)
        within the date range specified by `self._start_date` and `self._end_date`. It then combines
        the data into a single DataFrame, with an additional 'TIC' column indicating the instrument
        for each row of data.

        Returns:
            None

        Raises:
            Exception: If there is an issue with downloading the data for any instrument, an exception
                    is caught, and an error message is logged with details about the problem.

        Note:
            This function uses the Yahoo Finance API (yfinance) to download historical stock price data
            for multiple instruments, excluding 'MM.NS', which is checked for separately. The data is
            concatenated into a single DataFrame named `self._all_data`, making it easy to work with
            the combined data.

        Example:
            To load historical data for a list of equities within a specified date range and combine
            them into a single DataFrame, you can call the function like this:

            >>> load_data()
        """
        try:
            self._all_data = pd.DataFrame()

            if len(glob.glob(os.path.join("data", f"ALLDATA{''.join(self._index.split('/'))}_{datetime.datetime.now().date().strftime('%d%b%Y')}.csv"))) > 0:
                self._all_data = pd.read_csv(f"data/ALLDATA{''.join(self._index.split('/'))}_{datetime.datetime.now().date().strftime('%d%b%Y')}.csv", index_col=0, parse_dates=True)[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'TIC']]
            else:
                for equity in self._tickers:
                    if equity != "MM.NS":
                        data = yf.download(equity, start=self._start_date, end=self._end_date, progress=False).dropna()
                        data['TIC'] = equity
                        self._all_data = pd.concat([self._all_data, data])
                        logger.info(f"Equity Downloading = {equity}, len = {len(self._all_data)}")
                # save the all data 
                self.save_file()
        except Exception as e:
            logger_data.info(f"problem {e} in load_data() at line no.={get_exception_line_no()}")


    def load_baseline(self) -> None:
        """
        Load baseline financial data for a specified index from Yahoo Finance.

        This method attempts to download historical financial data for a specific stock or index
        within the given date range and assigns it to the '_baseline' attribute of the object.

        :raises Exception: If there is an issue during the data download process, an exception is raised.
        
        :return: None
        """
        try:
            # loading the baseline data
            self._baseline = yf.download(tickers=self._index_dictionary[self.getIndex()][0], start=self._start_date, end=self._end_date, progress=False)
        except Exception as e:
            logger_data.info(f"problem {e} in load_baseline() at line no.={get_exception_line_no()}")


    def load_all_index_tickers(self) -> None:
        """
        Load a list of tickers for a specified financial index.

        This method retrieves a list of tickers associated with a given financial index.
        It can obtain tickers in different ways based on the availability of data sources
        and market information.

        If a valid expression is provided for the index in the '_index_dictionary' and the
        market is checked to be valid using 'check_market', the method attempts to load
        tickers using the 'make_ticker_nse' function on the evaluated expression.
        
        If no expression is provided for the index, but the market is valid, it loads
        tickers from a CSV file named 'NSE550.csv' stored in the 'datastore' directory.

        If none of the above conditions are met, it assigns the ticker data from the index
        dictionary as-is.

        :raises Exception: If there is an issue during the ticker loading process, an exception is raised.
        
        :return: None
        """
        try:
            # load all tickers inside a given index
            if eval(self._index_dictionary[self.getIndex()][1]) != None and check_market(self._index):
                self._tickers = make_ticker_nse(eval(self._index_dictionary[self.getIndex()][1]))
            elif eval(self._index_dictionary[self.getIndex()][1]) == None and check_market(self._index):
                self._tickers = make_ticker_nse_bse(pd.read_csv('datastore/NSE_BSE_LIST.csv'))
            else:
                self._tickers = eval(self._index_dictionary[self.getIndex()][1])
        except Exception as e:
            logger_data.info(f"problem {e} in load_all_index_tickers() at line no.={get_exception_line_no()}")


    def getIndex(self) -> None:
        """
        Get the financial index associated with the object.

        This method retrieves the financial index associated with the object and returns it as a string.

        :return: A string representing the financial index.
        :rtype: str
        """
        try:
            return self._index
        except Exception as e:
            logger_data.info(f"problem {e} in getIndex() at line no.={get_exception_line_no()}")


    def getIndexData(self) -> pd.DataFrame:
        """
        Get the baseline financial data associated with the object's financial index.

        This method retrieves and returns the baseline financial data associated with the financial index
        represented by the object. The data is returned as a Pandas DataFrame.

        :return: A Pandas DataFrame containing the baseline financial data.
        :rtype: pd.DataFrame
        """
        try:
            return self._baseline
        except Exception as e:
            logger_data.info(f"problem {e} in getIndexData() at line no.={get_exception_line_no()}")


    def resampler(self, df:pd.DataFrame=pd.DataFrame(), dataType:str="baseline", frequency:str="M") -> pd.DataFrame:
        """
        Resample financial data to a specified frequency.

        This method resamples a given DataFrame or the baseline financial data associated with the object's
        financial index to a specified frequency. The resampled data is returned as a Pandas DataFrame.

        :param df: The DataFrame to be resampled (optional). If not provided, the baseline data is used.
        :type df: pd.DataFrame, optional

        :param dataType: The type of data to be resampled. Use "securities" to resample the provided DataFrame,
                        or "baseline" to resample the object's baseline financial data.
        :type dataType: str, optional

        :param frequency: The frequency to which the data should be resampled (e.g., "M" for monthly).
        :type frequency: str

        :return: A Pandas DataFrame containing the resampled financial data.
        :rtype: pd.DataFrame
        """
        try:
            if dataType == "securities":
                return self.resample_df(df, frequency=frequency)
            elif dataType == "baseline":
                return self._baseline.resample(frequency).last().dropna()
        except Exception as e:
            logger_data.info(f"problem {e} in resampler() at line no.={get_exception_line_no()}")


    def resample_df(self, _data, frequency) -> pd.DataFrame:
        """
        Resample a given DataFrame to a specified frequency.

        This method resamples a given DataFrame to a specified frequency, retaining the last valid observation
        for each resampling period. The resampled data is returned as a Pandas DataFrame.

        :param _data: The DataFrame to be resampled.
        :type _data: pd.DataFrame

        :param frequency: The frequency to which the data should be resampled (e.g., "M" for monthly).
        :type frequency: str

        :return: A Pandas DataFrame containing the resampled data.
        :rtype: pd.DataFrame
        """
        try:
            return _data.resample(frequency).last().dropna()
        except Exception as e:
            logger_data.info(f"problem {e} in resample_df() at line no.={get_exception_line_no()}")


    def getAllindextickers(self) -> list:
        """
        Get a list of all tickers associated with the object's financial index.

        This method retrieves and returns a list of all tickers associated with the financial index
        represented by the object. The tickers are returned as a list of strings.

        :return: A list of strings containing all tickers for the financial index.
        :rtype: list
        """
        try:
            return self._tickers
        except Exception as e:
            logger_data.info(f"problem {e} in getAllindextickers() at line no.={get_exception_line_no()}")


    def getAllindexdata(self) -> pd.DataFrame:
        """
        Get all financial data associated with the object's financial index.

        This method retrieves and returns all financial data associated with the financial index
        represented by the object. The data is returned as a Pandas DataFrame.

        :return: A Pandas DataFrame containing all financial data for the financial index.
        :rtype: pd.DataFrame
        """
        try:
            return self._all_data
        except Exception as e:
            logger_data.info(f"problem {e} in getAllindexdata() at line no.={get_exception_line_no()}")

    
    def save_file(self) -> None:
        """
        Saves the all data file.
        """
        self._all_data.to_csv(f"data/ALLDATA{''.join(self._index.split('/'))}_{datetime.datetime.now().date().strftime('%d%b%Y')}.csv")
