# Import Statements

from rich import print as rprint
from rich import box
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.markdown import Markdown
from rich.terminal_theme import MONOKAI
from rich.theme import Theme
from rich.table import Table
from utils import df_to_table, filter_database

import numpy as np
from screener_investor import MarketScreener

# Header
print("\n\n")
console = Console()

markdown = Markdown("## WELCOME TRADERS")
console.print(markdown, style="bold yellow", highlight=True)
print("\n")


state = True

while state:
    # Lookback Period Input
    mark_lookback = Markdown("\n- Enter lookback period in days(Default is 365 i.e. 1 year): ")
    console.print(mark_lookback, style="bold yellow")
    lookback = int(Prompt.ask('[bold red] >>> [/bold red]'))


    prefer_markdown = Markdown("\n\n1. Stock Screener\n2. Baseline Performance\n3. Individual Stock Details\n4. Asset Allocation\n5. Correlation Check\n6. Exit\n")
    console.print(prefer_markdown, style="bold magenta")
    prefer = str(Prompt.ask('[bold red] >>> [/bold red]'))

    # Driver Code
    if prefer == "1":
        index_markdown = Markdown("\n- Enter your preferred Index Name\n\n")
        console.print(index_markdown, style="bold blue")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index_option_md = Markdown('1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE All\n10. NSE Custom\n')
        console.print(index_option_md, style="bold green")
        index = indexes[int(Prompt.ask('[bold red] >>> [/bold red]')) - 1]

        obj = MarketScreener(index, lookback=lookback)
        dataf = obj._index_stocks_stats()
        dataf.set_index('TIC', inplace=True)
        dataf = dataf.astype('float')

        for cols in dataf.columns:
            dataf[cols] = dataf[cols].apply(lambda x: np.around(x, 2))

        dataf = dataf.reset_index()

        # Show tables
        table = Table(show_header=True,  header_style="bold magenta", style="green")
        table = df_to_table(dataf, table)
        table.row_styles = ["none", "dim"]
        table.box = box.ROUNDED
        console.print(table)

        save = str(Confirm.ask("\n[bold green] Want it in an Excel file[/bold green]")).strip().upper()

        if save == "Y":
            dataf.to_excel(f"{index}.xlsx", index=False)

        use_filter = True
        temp = dataf.copy()

        while use_filter:
            filter_mark = Markdown("\n- Enter your screening conditions\n\n- Note:\n1. Enter conditions seperated by _. For Eg: Annual Volatility greater than 40% can be written as AV_>_40\n2. SR-Sharpe Ratio\t- AV-Annual Volatility\t- MDD-Maximum Drawdown\t- VaR-Value at Risk\t- cVaR-Conditional Value at Risk\t- SC-Score\n")
            console.print(filter_mark, style="bold blue")
            filters = str(Prompt.ask("\n[bold red] >>> [/bold red]")).split()

            # Filters by input
            temp = filter_database(temp, filters)

            # Show tables
            table1 = Table(show_header=True,  header_style="bold magenta", style="green")
            table1 = df_to_table(temp, table1)
            table1.row_styles = ["none", "dim"]
            table1.box = box.ROUNDED
            console.print(table1)
            use_filter = False


    # Next Baseline
    if prefer == "2":
        index_markdown = Markdown("\n- Enter your preferred Index Name\n\n")
        console.print(index_markdown, style="bold blue")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index_option_md = Markdown('1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE All\n10. NSE Custom\n')
        console.print(index_option_md, style="bold green")
        index = indexes[int(Prompt.ask('[bold red] >>> [/bold red]')) - 1]

        obj = MarketScreener(index, lookback=lookback)
        dataf = obj.get_baseline_stats()

        for cols in dataf.index[2:]:
            dataf.loc[cols] = dataf.loc[cols].apply(lambda x: np.around(float(x), 2))

        dataf.reset_index(inplace=True)
        dataf.rename(columns={'index': 'Metric'}, inplace=True)
        # Show tables
        table = Table(show_header=True,  header_style="bold magenta", style="green")
        table = df_to_table(dataf, table)
        table.row_styles = ["none", "dim"]
        table.box = box.ROUNDED
        console.print(table)


    # Details Individual Stocks
    if prefer == "3":
        index_markdown = Markdown("\n- Enter your preferred Index Name\n\n")
        console.print(index_markdown, style="bold blue")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index_option_md = Markdown('1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE All\n10. NSE Custom\n')
        console.print(index_option_md, style="bold green")
        index = indexes[int(Prompt.ask('[bold red] >>> [/bold red]')) - 1]

        obj = MarketScreener(index, lookback=lookback)
        print("\n")
        tick = str(Prompt.ask('[bold green] Enter ticker symbol [/bold green]'))
        df = obj.individual_details(tick)
        print("\n")
        for cols in df.columns[1:]:
            df[cols] = df[cols].apply(lambda x: np.around(float(x), 2))

        # Show tables
        table = Table(show_header=True,  header_style="bold magenta", style="green")
        table = df_to_table(df, table)
        table.row_styles = ["none", "dim"]
        table.box = box.ROUNDED
        console.print(table)


    # Asset Allocation
    if prefer == "4":
        cash = (Prompt.ask('\n[bold red] Enter Cash [/bold red]')).strip()
        if cash.isnumeric():
            cash = float(cash)

            # Optimisation method check
            index_option_md = Markdown('1. Max Sharpe\n2. Kelly\n3. HRP\n4. Min Vol\n')
            console.print(index_option_md, style="bold blue")

            option = Prompt.ask("\n[bold green] Enter Option [/bold green]").strip()
            if option == "1":
                method = "max_sharpe"
            elif option == "2":
                method = "kelly"
            elif option == "3":
                method = "HRP"
            elif option == "4":
                method = "min_vol"
            else:
                print("You have given an invalid response\n")
                print("Enter a valid response")

            # Shrinkage Method
            index_option_md = Markdown('1. Ledoit Wolf\n2. Semi Variance\n3. Sample Covariance\n4. Exp. Covariance\n')
            console.print(index_option_md, style="bold blue")

            option = Prompt.ask("\n[bold green] Enter Option [/bold green]").strip()
            if option == "1":
                shrinkage = "ledoit_wolf"
            elif option == "2":
                shrinkage = "semicovariance"
            elif option == "3":
                shrinkage = "sample_cov"
            elif option == "4":
                shrinkage = "exp_cov"
            else:
                print("You have given an invalid response\n")
                print("Enter a valid response")

            num_stocks = min(int(Prompt.ask("\n[bold cyan] Enter the number of unique stocks for portfolio construction (Max. 10) [/bold cyan]")), 10)

            stock_names = []
            for i in range(num_stocks):
                console.print(f"\n[bold green] Enter Symbol No.{i+1} [/bold green]")
                stock_names.append(Prompt.ask("[bold red] >>> [/bold red]").strip().upper())

            gre_lin = Prompt.ask("\n[bold magenta] Enter G for Greedy Portfolio and L for Linear Portfolio:\n\n Enter Option [/bold magenta] ").upper().strip()
            print("\n")
            if gre_lin == "G":
                alloc = "Greedy"
            elif gre_lin == "L":
                alloc = "Linear"

            index_markdown = Markdown("\n- Enter your preferred Index Name\n\n")
            console.print(index_markdown, style="bold blue")

            indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
            index_option_md = Markdown('1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE All\n10. NSE Custom\n')
            console.print(index_option_md, style="bold green")
            index = indexes[int(Prompt.ask('[bold red] >>> [/bold red]')) - 1]

            obj = MarketScreener(index, lookback=lookback)
            freq = Prompt.ask('\n[bold yellow] Enter Allocation Frequency (M-Monthly, D-Daily) [/bold yellow]').upper().strip()
            A = obj.asset_allocation(cash, stock_names, method, shrinkage, alloc, freq)
            
            # Show tables
            table = Table(show_header=True,  header_style="bold magenta", style="green")
            table = df_to_table(A, table)
            table.row_styles = ["none", "dim"]
            table.box = box.ROUNDED
            console.print(table)


    # Correlation Check
    if prefer == "5":

        num_stocks_corr = min(int(Prompt.ask("\n[bold cyan] Enter the number of unique stocks for portfolio construction (Max. 10) [/bold cyan]")), 10)

        stock_names_corr = []
        for i in range(num_stocks_corr):
            console.print(f"\n[bold green] Enter Symbol No.{i+1} [/bold green]")
            stock_names_corr.append(Prompt.ask("[bold red] >>> [/bold red]").strip().upper())

        index_markdown = Markdown("\n- Enter your preferred Index Name\n\n")
        console.print(index_markdown, style="bold blue")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index_option_md = Markdown('1. Nifty 50\n2. Bank Nifty\n3. Nasdaq\n4. S&P500\n5. FTSE250\n6. FTSE100\n7. DOW\n8. IBOVESPA\n9. NSE All\n10. NSE Custom\n')
        console.print(index_option_md, style="bold green")
        index = indexes[int(Prompt.ask('[bold red] >>> [/bold red]')) - 1]

        obj = MarketScreener(index, lookback=lookback)
        A = obj.corr_cals(stock_names_corr)
        A = A.astype('float').round(2).reset_index()
        A.rename(columns={f'{A.columns[0]}': ''}, inplace=True)

        # Show tables
        table = Table(show_header=True,  header_style="bold magenta", style="green")
        table = df_to_table(A, table)
        table.row_styles = ["none", "dim"]
        table.box = box.ROUNDED
        console.print(table)


    # Continue to use the screener
    if prefer == "6":
        console.print("[bold yellow] Exiting... [/bold yellow]")
        break
