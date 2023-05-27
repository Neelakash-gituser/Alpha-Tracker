# Import Statements

from utils.utils import df_to_table, filter_database
from investor import MarketScreener
from display import displayDf, displayString, rules, panelShow

import numpy as np


Done = False

while not Done:
    # Start
    panelShow(text="Investment Research Platform", style="bold blue")

    # Show the options
    indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE']
    index = indexes[int(displayString("Choose the Index:\n\n1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE\n\nEnter Index Code", 
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
        option = displayString("\n1.Baseline Performance\n2.All Stock Performance\n3.Screen Stocks\n\nEnter Code", style="bold red")
        frequency = displayString("\nEnter Frequency of Investing (D/W/M/Y)", style="bold red").upper()

        # initialise everything at beginning once
        if not initialised:
            investor._select_index()
            investor._index_stocks_stats(frequency)
            initialised = True

        # functions
        functionalities = {"1": investor.get_baseline_stats(frequency), "2": investor.getAllDetails()[0]}

        df = functionalities[option]
        displayDf(df)
        break
    break
