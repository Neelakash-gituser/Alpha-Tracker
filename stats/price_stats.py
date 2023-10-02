import numpy as np
import pandas as pd

from logger._logger import logger, get_exception_line_no
from financiallib.statistical_tests import var_historic, cvar_historic

logger_stats = logger.getLogger("stats")


def getPricestats(df:pd.DataFrame, frequency="M", date_col="Date", price_col="Adj Close") -> tuple:
    """
    Calculate various price statistics from a given DataFrame.

    This function calculates and returns various statistics related to historical price data from
    a DataFrame, including annual return, annual volatility, Sharpe ratio, maximum drawdown, Value at Risk (VaR),
    Conditional Value at Risk (CVaR), and more.

    :param df: The DataFrame containing historical price data.
    :type df: pd.DataFrame

    :param frequency: The frequency of the data (e.g., "M" for monthly).
    :type frequency: str, optional

    :param date_col: The name of the column containing date information.
    :type date_col: str, optional

    :param price_col: The name of the column containing price information.
    :type price_col: str, optional

    :return: A tuple containing various price statistics including start date, end date, number of periods,
             annual return, annual volatility, Sharpe ratio, maximum drawdown, Value at Risk (VaR), Conditional
             Value at Risk (CVaR), the last one-period change, highest price, lowest price, and current price.
    :rtype: tuple
    """
    try:
        # Will work on a copy of the sent df
        _df = df.copy()
        
        time_tracker = {"D":1, "M":30, "Q":90, "W":7, "Y":365}
        multiplier = {"D":252, "M":12, "Q":4, "W":5, "Y":1}

        # calculate stats
        startDate, endDate = _df[date_col].iloc[0], _df[date_col].iloc[-1]
        no_of_periods = (pd.to_datetime(endDate) - pd.to_datetime(startDate)).days // time_tracker[frequency]

        # Annual Return
        ret = _df[price_col].pct_change().fillna(0)
        cumret = (1 + ret).prod() - 1
        annual_ret = (cumret / no_of_periods) * multiplier[frequency]

        # Annual Volatility
        annual_vol = np.std(_df[price_col].pct_change().fillna(0)) * np.sqrt(multiplier[frequency])

        # Sharpe Ratio
        sharpe = annual_ret / annual_vol

        # Drawdown
        inv = pd.Series(_df[price_col].values)

        z = pd.Series(index=range(len(inv)))
        z.iloc[0] = inv.iloc[0]

        for i in range(1, len(inv)):
            z.iloc[i] = max(inv[i], z[i-1])

        # Maximum Drawdown
        drawdowns = (inv - z)
        max_drawdown = drawdowns.min() / z.iloc[0]

        # last 1 period change
        ret_1_ch = _df[price_col].pct_change().fillna(0).iloc[-1]

        # var and cVar
        var = var_historic(_df[price_col].pct_change().dropna())
        cvar = cvar_historic(_df[price_col].pct_change().dropna())

        # Highest and Lowest price
        high, low = _df[price_col].max(), _df[price_col].min()

        # current price
        current_price = _df[price_col].iloc[-1]

        return startDate, endDate, no_of_periods, frequency, annual_ret, annual_vol, sharpe, max_drawdown, var, cvar, ret_1_ch, high, low, current_price
    except Exception as e:
        logger_stats.info(f"problem {e} in getPricestats() at line no.={get_exception_line_no()}")



# Correlation Calculator
def corr_cals(_df:pd.DataFrame, ticker_list:list) -> pd.DataFrame:
    """
    Calculate the correlation matrix between a list of ticker symbols based on adjusted close prices.

    This function calculates and returns the correlation matrix between a list of ticker symbols
    based on their adjusted close prices from a given DataFrame.

    :param _df: The DataFrame containing historical price data.
    :type _df: pd.DataFrame

    :param ticker_list: A list of ticker symbols to calculate correlations for.
    :type ticker_list: list

    :return: A Pandas DataFrame representing the correlation matrix between the ticker symbols.
    :rtype: pd.DataFrame
    """
    try:
        df = pd.DataFrame()

        for i in ticker_list:
            try:
                data = _df[_df['TIC']==i][['Adj Close', 'TIC']]
            except:
                pass

            df = pd.concat([df, data])

        df = df[['TIC', 'Adj Close']].reset_index().set_index(['Date', 'TIC']).unstack()
        df.columns = df.columns.droplevel(0)
        df.columns.name = None
        df = df.round(2)

        return df.corr()
    except Exception as e:
        logger_stats.info(f"problem {e} in corr_cals() at line no.={get_exception_line_no()}")

