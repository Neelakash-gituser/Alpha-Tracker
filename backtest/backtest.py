# Imports


# Intermediate Function
def backtestCalculator(cash:float, backtest_df:dict, weights:dict) -> tuple:
    amount_allocation = {}
    shares, balance, total_invested = {}, 0, 0
    prices = backtest_df

    # amount allocated for each stock or security
    for keys in backtest_df.keys():
        amount_allocation[keys] = weights[keys] * cash

    # No. of shares that can be bought using that amount
    for keys in backtest_df.keys():
        shares[keys] = (amount_allocation[keys] // prices[keys])

    # total invested amount
    for keys in backtest_df.keys():
        total_invested = total_invested + (shares[keys] * prices[keys])

    # update cash , balance and total investment
    balance = cash - total_invested

    return total_invested, balance, shares