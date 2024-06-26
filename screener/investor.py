import os
import datetime
import pandas as pd
import datetime as dt

from rich.progress import track
from utils.utils import filter_database
from logger._logger import logger, get_exception_line_no
from dataloader.data_loader import Dataloader
from stats.price_stats import getPricestats, corr_cals
from portfolio_allocation.allocator import asset_allocation

logger = logger.getLogger("investor_module")

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
                    # beta of the stock 
                    beta = self.calculate_beta(price_series=data, baseline_price_series=self._baseline)
                    
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
                                f'{self._currency} {round(current_price, 2)}',
                                f'{round(beta, 2)}'
                                ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                        'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough', 'Current Price', 'Beta'], columns=[f'{tick}'])
                    
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
                                round(low, 2),
                                round(current_price, 2),
                                round(beta, 2)
                                ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                        'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough', 'Current Price', 'Beta'], columns=[f'{tick}'])
                    
                    self._visual_data = pd.concat([self._visual_data, df.T])
                    self._filter_data = pd.concat([self._filter_data, newDf.T])
                
                except:
                    pass

            # saves the dataframe
            self.save_index_stats() 
        except:
            pass


    # More info on individual stocks
    def individual_details(self, stock_name, frequency):
        # Fetch Data and take details
        data = self._data_loader.resampler(df=self._data_loader.load_single_instrument(stock_name=stock_name), dataType="securities", frequency=frequency)
        startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price = getPricestats(df=data.reset_index(), 
                                                                                                                                                                  frequency=frequency)
        # calculate stock beta
        beta = self.calculate_beta(price_series=data, baseline_price_series=self._baseline)

        # Mapper                                                                                                                                                    
        tracker = {"D":"Days", "M":"Months", "W":"Weeks", "Q":"Quarters", "Y":"Years"}
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
                            f'{self._currency} {round(current_price, 2)}',
                            f'{round(beta, 2)}'
                            ], index=['Start Date', 'End Date', f'Period (in {tracker[frequency]})', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio', 
                                    'Maximum Drawdown', 'VaR', 'cVaR', f'1 {tracker[frequency][:-1]} Change (%)', 'Highest Peak', 'Lowest Trough', 'Current Price', 'Beta'], columns=[f'{stock_name}'])
        
        return df.T


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
    

    def assetAllocation(self, cash:float, opt_method:str, use_method:str, frequency:str, value_col:str, stock_list:list) -> pd.DataFrame:
        # price data
        price_data = self._data_loader.getAllindexdata()[[value_col, 'TIC']].reset_index().set_index(['Date', 'TIC']).unstack()
        price_data.columns = price_data.columns.droplevel()
        price_data.columns.name = None

        # take only mentioned tickers
        price_data = price_data[stock_list]

        # resample to frequency
        price_data = self._data_loader.resample_df(price_data, frequency=frequency)
        
        # get the allocations
        allocations = asset_allocation(cash=cash, df=price_data, opt_method=opt_method, frequency=frequency, use_method=use_method)

        return allocations
    
    def correlation_matrix(self, stock_list:list, frequency:str, value_col:str) -> pd.DataFrame:
        # correlation matrix
        price_data = self._data_loader.getAllindexdata()[[value_col, 'TIC']].reset_index().set_index(['Date', 'TIC']).unstack()
        price_data.columns = price_data.columns.droplevel()
        price_data.columns.name = None

        # take only mentioned tickers
        price_data = price_data[stock_list]
        
        # resample to frequency
        price_data = self._data_loader.resample_df(price_data, frequency=frequency)
        corr_df = corr_cals(price_data)
        return corr_df

    def filterDatabase(self, filters:list, frequency:str) -> pd.DataFrame:
        return filter_database(self._filter_data, filters=filters, frequency=frequency)

    def getAllDetails(self) -> tuple:
        return self._visual_data, self._filter_data
    
    def getAllindexdata(self) -> pd.DataFrame:
        return self._all_stocks
    
    def save_index_stats(self) -> None:
        try:
            self._visual_data.to_excel(f"data/statsdata/STATS{(''.join(self.indexes.split('/')))}_{datetime.datetime.now().date().strftime('%d%b%Y')}.xlsx")
        except Exception as e:
            logger.info(f"save_index_stats() - {e} in line no. = {get_exception_line_no()}, index = {self.indexes}")

    def calculate_beta(self, price_series:pd.Series, baseline_price_series:pd.Series) -> None:
        """
        Calculates the beta of stocks.
        """
        try:
            price_returns = price_series['Adj Close'].pct_change() # calculate price returns
            baseline_returns = baseline_price_series['Adj Close'].pct_change() # calculate baseline price return
            covariance = price_returns.cov(baseline_returns)

            # return the beta of the stock.
            return covariance / baseline_returns.var()
        except Exception as e:
            logger.info(f"problem inside calculate_beta() - {e}, at line no. = {get_exception_line_no()}")