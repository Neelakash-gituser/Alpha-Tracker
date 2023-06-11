# Import Statements

from utils.utils import df_to_table, filter_database
from investor import MarketScreener
from display import displayDf, displayString, rules, panelShow

import numpy as np


Done = False

# Start
panelShow(text="Investment Research Platform", style="bold blue")

while not Done:
    # state manager
    manager = {"y":True, "n":False}

    # Show the options
    indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE']
    index = indexes[int(displayString("\n\nChoose the Index:\n\n1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE\n\nEnter Index Code", 
                                      style="bold magenta")) - 1]

    # choose lookback period
    lookback = int(displayString("\nEnter lookback period (in Days)", style="bold green"))

    # New Section
    rules(text="Functionalities")

    # create the investor
    investor = MarketScreener(indexes=index, lookback=lookback)

    state = True
    initialised = False

    while state:
        # show all options
        option = displayString("\n1. Baseline Performance\n2. All Stock Performance\n3. Screen Stocks\n4. Asset Allocation\n\nEnter Code", style="bold magenta")
        frequency = displayString("\n\nEnter Frequency of Investing (D/W/M/Y)", style="bold blue").upper()

        # initialise everything at beginning once
        if not initialised:
            investor._select_index()
            investor._index_stocks_stats(frequency)
            initialised = True

        # functions
        functionalities = {"1": investor.get_baseline_stats(frequency), "2": investor.getAllDetails()[0]}
        exclude_list = ["3", "4"]

        if option not in exclude_list:
            df = functionalities[option]
            displayDf(df)

        elif option == "3":
            filters = displayString(f"\n\nEnter filtering criteria for screening {index} stocks\n\nNote: Enter all screening criteria as AV_<_30 (This means show all stocks with annual volatility less than 30%) \
                                    \n\n1. 1PC (1 Period Change)\n2. AR (Annual Return) \
                                    \n3. SR (Sharpe Ratio)\n4. MDD (Max Drawdown)\n5. VaR\n6. cVaR\n7. HP (Highest Peak)\n8. LT (Lowest Trough)\n9. CP (Current Price)\n10. AV (Annual Volatility)\n\nEnter Conditions", 
                                     
                                    style="bold blue").split()
            
            # screen stocks
            df = investor.filterDatabase(filters, frequency)
            displayDf(df)

        elif option == "4":
            # method mappers
            opt_method_dict = {"1":"max_sharpe", "2":"min_vol", "3":"kelly", "4": "HRP"}
            use_method_dict = {"1":"ledoit_wolf", "2":"semicovariance", "3":"sample_cov", "4": "exp_cov"}

            cash = float(displayString("\nEnter Cash Amount", style="bold yellow"))
            opt_method = opt_method_dict[displayString("\n1. Max Sharpe\n2. Min Vol\n3. Kelly\n4. HRP\n\nEnter Code", style="bold magenta")]
            use_method = use_method_dict[displayString("\n1. Ledoit Wolf\n2. Semi-Covariance\n3. Sample Covariance\n4. Exponential Covariance\n\nEnter Code", style="bold green")]
            stock_list = displayString("\nEnter Stock Tickers\nEnter Code", style="bold magenta").upper().split()
            
            # call method
            dataFrame = investor.assetAllocation(cash=cash, opt_method=opt_method, use_method=use_method, frequency=frequency, value_col="Adj Close", stock_list=stock_list)

            displayDf(dataFrame)
        
        state = manager[displayString("\nKeep exploring the same index ? [y/n]", style="bold green").lower()]

    # continue using screener check
    Done = not manager[displayString("\nExplore some new index ? [y/n]", style="bold green").lower()]
