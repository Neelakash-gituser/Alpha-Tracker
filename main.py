# Import Statements

from rich import box
from rich.layout import Layout
from rich.console import Console
from rich.table import Table
from utils.utils import df_to_table, filter_database
from investor import MarketScreener

import numpy as np


Done = False

while not Done:
    # Show the options
    indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE']
    index = indexes[int(input("Choose the Index:\n\n1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE\n\n>>> ")) - 1]

    # choose lookback period
    lookback = int(input("\nEnter lookback period (in Days): "))

    # create the investor
    investor = MarketScreener(indexes=index, lookback=lookback)

    state = True
    initialised = False

    while state:
        # show all options
        option = input("\n1.Baseline Performance\n2.All Stock Performance\n3.Screen Stocks\n\n>>> ")
        frequency = input("\nEnter Frequency of Investing (D/W/M/Y): ").upper()

        # initialise everything at beginning once
        if not initialised:
            investor._select_index()
            investor._index_stocks_stats(frequency)
            initialised = True

        functionalities = {"1": investor.get_baseline_stats(frequency), "2": investor.getAllDetails()[0]}

        df = functionalities[option]

        print("\n", df)
        break
    break
