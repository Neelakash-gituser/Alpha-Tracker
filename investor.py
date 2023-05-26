import os
import pandas as pd
import datetime as dt


from rich.progress import track
from utils.utils import filter_database
from dataloader.data_loader import Dataloader
from stats.price_stats import getPricestats

# from numpy.linalg import inv
# from pypfopt import risk_models
# from pypfopt import expected_returns
# from pypfopt import EfficientFrontier
# from pypfopt import objective_functions
# from pypfopt.risk_models import risk_matrix
# from pypfopt.hierarchical_portfolio import HRPOpt
# from yahoo_fin import stock_info as sf
# from financiallib.utils import drawdown
# from financiallib.statistical_tests import var_historic, cvar_historic



class MarketScreener:

    # Constructor
    def __init__(self, indexes:str, lookback:int=365, currency:str="₹") -> None:
        self.start = dt.datetime.now() - dt.timedelta(days=lookback)
        self.end = dt.datetime.now()
        self.indexes = indexes
        self.lookback = lookback
        self._currency = currency

        # some dataframe that will live throughout the life of the object
        self._baseline = pd.DataFrame()
        self._all_stocks = pd.DataFrame()

        # creates the data directory
        os.makedirs("data", exist_ok=True)

        # initiate data_loader class and load all data
        self._data_loader = Dataloader(index=self.indexes, start_date=self.start, end_date=self.end)
        self._data_loader.load_baseline()
        self._data_loader.load_all_index_tickers()
        self._data_loader.load_data()



    # load the index data and all tickers
    def _select_index(self) -> None:
        # Get all stocks in a particular index and load index data
        self._tickers = self._data_loader.getAllindextickers()

        # Get the baseline index data
        self._baseline = self._data_loader.getIndexData()



    # Baseline information
    def _baseline_stats(self, frequency) -> tuple:
        # get all basic stats
        baselineResampled = self._data_loader.resampler(dataType="baseline", frequency=frequency)
        startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price = getPricestats(df=baselineResampled.reset_index(), 
                                                                                         frequency=frequency, date_col="Date", price_col="Adj Close")
        
        return startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price


    # Info of all stocks in the index
    def _index_stocks_stats(self, frequency) -> None:
        # get all index data
        try:
            self._all_stocks = self._data_loader.getAllindexdata()
            self._all_stocks.sort_index(inplace=True)

            tracker = {"D":"Days", "M":"Months", "W":"Weeks", "Q":"Quarters", "Y":"Years"}
            self._visual_data = pd.DataFrame()
            self._filter_data = pd.DataFrame()

            # get stats for all data
            for tick in track(self._tickers, description='[green]Processing Data'):
                try:
                    data = self._all_stocks[self._all_stocks['TIC']==tick]
                    resamp = self._data_loader.resampler(data, frequency=frequency, dataType="securities")
                    startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price = getPricestats(resamp.reset_index(), 
                                                                                                                                    frequency=frequency, date_col="Date", price_col="Adj Close")
                    
                    df = pd.DataFrame([
                                startDate.strftime("%Y-%m-%d"),
                                endDate.strftime("%Y-%m-%d"),
                                round(no_of_periods),
                                f'{round(annual_ret*100, 2)}%',
                                f'{round(annual_vol*100, 2)}%',
                                f'{round(sharpe, 2)}',
                                f'{round(max_drawdown*100, 2)}%',
                                f'{round(var*100, 2)}%',
                                f'{round(cvar*100, 2)}%',
                                f'{round(ret_1_ch*100, 2)}%',
                                f'{self._currency} {round(high, 2)}',
                                f'{self._currency} {round(low, 2)}',
                                f'{self._currency} {round(current_price, 2)}'
                                ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                        'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough', 'Current Price'], columns=[f'{tick}'])
                    
                    newDf = pd.DataFrame([
                                startDate.strftime("%Y-%m-%d"),
                                endDate.strftime("%Y-%m-%d"),
                                round(no_of_periods),
                                round(annual_ret*100, 2),
                                round(annual_vol*100, 2),
                                round(sharpe, 2),
                                round(max_drawdown*100, 2),
                                round(var*100, 2),
                                round(cvar*100, 2),
                                round(ret_1_ch*100, 2),
                                round(high, 2),
                                round(low, 2)
                                ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                        'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough'], columns=[f'{tick}'])
                    
                    self._visual_data = self._visual_data.append(df.T)
                    self._filter_data = self._filter_data.append(newDf.T)
                except:
                    pass
        except:
            pass



    # More info on individual stocks
    def individual_details(self, stock_name):
        pass



    # Just a function to aggregate our results.
    def get_baseline_stats(self, frequency:str) -> pd.DataFrame:
        # create a dataframe 
        tracker = {"D":"Days", "M":"Months", "W":"Weeks", "Q":"Quarters", "Y":"Years"}
        startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price = self._baseline_stats(frequency=frequency)

        return pd.DataFrame([
                             startDate.strftime("%Y-%m-%d"),
                             endDate.strftime("%Y-%m-%d"),
                             round(no_of_periods),
                             f'{round(annual_ret*100, 2)}%',
                             f'{round(annual_vol*100, 2)}%',
                             f'{round(sharpe, 2)}',
                             f'{round(max_drawdown*100, 2)}%',
                             f'{round(var*100, 2)}%',
                             f'{round(cvar*100, 2)}%',
                             f'{round(ret_1_ch*100, 2)}%',
                             f'{self._currency} {round(high, 2)}',
                             f'{self._currency} {round(low, 2)}',
                             f'{self._currency} {round(current_price, 2)}'
                             ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                       'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough', 'Current Price'], columns=['Summary'])
    


    def filterDatabase(self, filters) -> pd.DataFrame:
        return filter_database(self._filter_data, filters=filters)

    def getAllDetails(self) -> tuple:
        return self._visual_data, self._filter_data
    
    def getAllindexdata(self) -> pd.DataFrame:
        return self._all_stocks
