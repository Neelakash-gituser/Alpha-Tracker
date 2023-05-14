# # Intermediate Function
# def backtest(self, cash, backtest_df, weights):
#     amount_allocation = {}
#     shares, balance, total_invested = {}, 0, 0
#     prices = backtest_df

#     for keys in backtest_df.keys():
#         amount_allocation[keys] = weights[keys] * cash

#     for keys in backtest_df.keys():
#         shares[keys] = (amount_allocation[keys] // prices[keys])

#     for keys in backtest_df.keys():
#         total_invested = total_invested + (shares[keys] * prices[keys])

#     balance = cash - total_invested

#     return total_invested, balance, shares