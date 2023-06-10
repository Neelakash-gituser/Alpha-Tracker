# Imports
import pandas as pd
import numpy as np

from backtest.backtest import backtestCalculator
from numpy.linalg import inv
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier
from pypfopt import objective_functions
from pypfopt.risk_models import risk_matrix
from pypfopt.hierarchical_portfolio import HRPOpt


# Allocation of various stocks.
def asset_allocation(cash:float, df:pd.DataFrame, opt_method:str, frequency:str, use_method:str="ledoit_wolf") -> pd.DataFrame:

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
        num_shares = {'Invested': np.around(total_invested, 2), 'Balance': np.around(balance, 2), 'Expected Return': np.around(er, 2), 'Expected Volatility': np.around(ev, 2),
                                                                                                                                        'Expected Sharpe Ratio': np.around(es, 2)}
    else:
        num_shares = {'Invested': np.around(total_invested, 2), 'Balance': np.around(balance, 2)}

    num_shares.update(shares)
    new_final_df = pd.DataFrame(num_shares, index=[0])

    return new_final_df