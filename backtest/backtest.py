# Imports
from logger._logger import logger, get_exception_line_no

logger_backtset = logger.getLogger("backtest")


# Intermediate Function
def backtestCalculator(cash:float, backtest_df:dict, weights:dict) -> tuple:
    """
    Calculate the results of a backtest based on cash, stock prices, and allocation weights.

    This function performs a backtest using the provided cash, stock prices, and allocation weights.
    It calculates the total invested amount, the remaining balance, and the number of shares
    purchased for each stock.

    :param cash: The initial amount of cash available for investment.
    :type cash: float

    :param backtest_df: A dictionary containing stock symbols as keys and stock prices as values.
    :type backtest_df: dict

    :param weights: A dictionary containing stock symbols as keys and allocation weights as values.
    :type weights: dict

    :return: A tuple containing the total invested amount, the remaining balance, and a dictionary
             of shares purchased for each stock.
    :rtype: tuple
    """
    try:
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
    except Exception as e:
        logger_backtset.info(f"problem {e} in backtestCalculator() line no.={get_exception_line_no()}")