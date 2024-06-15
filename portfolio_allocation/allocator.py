# Imports
import pandas as pd
import numpy as np

from logger._logger import logger, get_exception_line_no
from backtest.backtest import backtestCalculator
from numpy.linalg import inv
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier
from pypfopt import objective_functions
from pypfopt.risk_models import risk_matrix
from pypfopt.hierarchical_portfolio import HRPOpt

logger_allocation = logger.getLogger("allocation")

# Allocation of various stocks.
def asset_allocation(cash:float, df:pd.DataFrame, opt_method:str, frequency:str, use_method:str="ledoit_wolf") -> pd.DataFrame:
    """
    Perform asset allocation optimization and return a DataFrame with investment details.

    This function performs asset allocation optimization based on historical price data and the chosen optimization
    method. It returns a DataFrame containing investment details, including invested amount, balance, and the number
    of shares allocated to each asset.

    :param cash: The initial amount of cash available for investment.
    :type cash: float

    :param df: The DataFrame containing historical price data for various assets.
    :type df: pd.DataFrame

    :param opt_method: The optimization method to use ("max_sharpe", "min_vol", "kelly", "HRP", or "EQ").
    :type opt_method: str

    :param frequency: The frequency of data (e.g., "M" for monthly).
    :type frequency: str

    :param use_method: The method for calculating the covariance matrix (default: "ledoit_wolf").
    :type use_method: str, optional

    :return: A Pandas DataFrame containing investment details, including invested amount, balance, and the number
             of shares allocated to each asset.
    :rtype: pd.DataFrame
    """
    try:
        # unique securities
        ticker_list = list(df.columns)

        df_cov = df.copy()
        mapper = {"D": 252, "M": 12, "W":52, "Q": 4, "Y": 1}
        freq = mapper[frequency]

        # convert datetime to string index
        df = df.reset_index()
        df['Date'] = df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
        df.set_index("Date", inplace=True)

        # Historical returns
        retu = expected_returns.mean_historical_return(df, frequency=freq)

        returns = retu
        mean_returns = returns
        cov = risk_matrix(df_cov, method=use_method)
        precision_matrix = pd.DataFrame(inv(cov), index=ticker_list, columns=ticker_list)  # Inverse of cov matrix

        # Optimisation Techniques
        if (opt_method.lower()=="max_sharpe"):

            ef = EfficientFrontier(retu, cov)
            weights = ef.nonconvex_objective(
                objective_functions.sharpe_ratio,
                objective_args = (ef.expected_returns, ef.cov_matrix),
                weights_sum_to_one=True,
            )
            er, ev, es = ef.portfolio_performance(verbose=False)
            wts = weights
            weights = wts

        elif (opt_method.lower()=="min_vol"):

            ef = EfficientFrontier(retu, cov, verbose=False)
            ef.add_objective(objective_functions.L2_reg, gamma=1)
            ef.min_volatility()
            wts = ef.clean_weights()
            er, ev, es = ef.portfolio_performance(verbose=False)
            weights = wts

        elif (opt_method.lower()=="kelly"):

            kelly_wt = precision_matrix.dot(mean_returns).clip(lower=0).values
            kelly_wt /= np.sum(np.abs(kelly_wt))
            wts = dict(zip(ticker_list, kelly_wt))
            weights = wts

        elif (opt_method.upper()=="HRP"):

            returns = df.pct_change().dropna()
            hrp = HRPOpt(returns)
            wts = hrp.optimize()
            wts = hrp.clean_weights()
            weights = wts

        elif (opt_method.upper()=="EQ"):

            wts = {s:1/len(ticker_list) for s in ticker_list}
            weights = wts

        else:
            print("Warning: Invalid optimisation method")


        # Discrete Allocation
        latest_prices = df.loc[df.index[-1]].to_dict()
        total_invested, balance, shares = backtestCalculator(cash, latest_prices, weights)

        if opt_method == "max_sharpe" or opt_method == "min_vol":
            num_shares = {'Invested (₹)': np.around(total_invested, 2), 'Balance (₹)': np.around(balance, 2), 'Expected Return (%)': f'{np.around(er, 2)*100}%', 
                                                                                                                'Expected Volatility (%)': f'{np.around(ev, 2)*100}%',
                                                                                                                'Expected Sharpe Ratio': np.around(es, 2),
                                                                                                                'Expected Portfolio Beta': 1}
        else:
            num_shares = {'Invested': np.around(total_invested, 2), 'Balance': np.around(balance, 2)}

        num_shares.update(shares)
        new_final_df = pd.DataFrame(num_shares, index=[0])

        return new_final_df
    
    except Exception as e:
        logger_allocation.info(f"problem {e} in asset_allocation() at line no.={get_exception_line_no()}")