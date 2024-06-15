import numpy as np
import pandas as pd
import scipy.stats

from scipy.stats import norm
from scipy.optimize import minimize
from logger._logger import logger, get_exception_line_no

logger_stats = logger.getLogger("stats")


def skewness(r:pd.Series) -> float:
    """
    Alternative to scipy.stats.skew()
    Computes the skewness of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**3).mean()
    return exp/sigma_r**3


def kurtosis(r:pd.Series) -> float:
    """
    Alternative to scipy.stats.kurtosis()
    Computes the kurtosis of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**4).mean()
    return exp/sigma_r**4


def is_normal(r, level=0.01) -> bool:
    """
    Applies the Jarque-Bera test to determine if a Series is normal or not
    Test is applied at the 1% level by default
    Returns True if the hypothesis of normality is accepted, False otherwise
    """
    if isinstance(r, pd.DataFrame):
        return r.aggregate(is_normal)
    else:
        statistic, p_value = scipy.stats.jarque_bera(r)
        return p_value > level


def var_historic(r:pd.Series, level=5) -> float:
    """
    Returns the historic Value at Risk at a specified level
    i.e. returns the number such that "level" percent of the returns
    fall below that number, and the (100-level) percent are above
    """
    if isinstance(r, pd.DataFrame):
        return r.aggregate(var_historic, level=level)
    elif isinstance(r, pd.Series):
        return -np.percentile(r, level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")


def cvar_historic(r:pd.Series, level=5) -> float:
    """
    Computes the Conditional VaR of Series or DataFrame
    """
    if isinstance(r, pd.Series):
        is_beyond = r <= -var_historic(r, level=level)
        return -r[is_beyond].mean()
    elif isinstance(r, pd.DataFrame):
        return r.aggregate(cvar_historic, level=level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")


def var_gaussian(r:pd.Series, level=5, modified=False) -> float:
    """
    Returns the Parametric Gauusian VaR of a Series or DataFrame
    If "modified" is True, then the modified VaR is returned,
    using the Cornish-Fisher modification
    """
    # compute the Z score assuming it was Gaussian
    z = norm.ppf(level/100)
    if modified:
        # modify the Z score based on observed skewness and kurtosis
        s = skewness(r)
        k = kurtosis(r)
        z = (z +
                (z**2 - 1)*s/6 +
                (z**3 -3*z)*(k-3)/24 -
                (2*z**3 - 5*z)*(s**2)/36
            )
    return -(r.mean() + z*r.std(ddof=0))


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
def corr_cals(_df:pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the correlation matrix between a list of ticker symbols based on adjusted close prices.

    This function calculates and returns the correlation matrix between a list of ticker symbols
    based on their adjusted close prices from a given DataFrame.

    :param _df: The DataFrame containing historical price data.
    :type _df: pd.DataFrame

    :return: A Pandas DataFrame representing the correlation matrix between the ticker symbols.
    :rtype: pd.DataFrame
    """
    try:
        _df = _df.pct_change()
        return _df.corr().round(2)
    
    except Exception as e:
        logger_stats.info(f"problem {e} in corr_cals() at line no.={get_exception_line_no()}")
















