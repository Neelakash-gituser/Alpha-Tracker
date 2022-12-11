from screener_investor import MarketScreener

print("="*150)
print("WELCOME TRADERS")
print("="*150)
print("\n\n")


state = True

while state:
    prefer = input("\n1.Stock Screener\n2.Baseline Performance\n3.Individual Stock Details\n4.Asset Allocation\n5.Correlation Check\n6.Exit\n\nOption: ").strip()

    # Driver Code
    if prefer == "1":
        print("\nEnter your preferred Index Name\n")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index = indexes[int(input('1.Nifty 50\n2.Bank Nifty\n3.Nasdaq\n4.S&P500\n5.FTSE250\n6.FTSE100\n7.DOW\n8.IBOVESPA\n9.NSE All\n10.NSE Custom\n>>> '))-1]

        obj = MarketScreener(index)
        dataf = obj._index_stocks_stats()
        print(dataf.head())
        save = input("\nWant it in an Excel file ? Y/N\n>>> ").strip().upper()
        if save == "Y":
            dataf.to_excel(f"{index}.xlsx", index=False)

        use_filter = True
        while use_filter:
            print("\nEnter your screening conditions\n\nNote:\n1.Enter conditions seperated by _. For Eg: Annual Volatility greater than 40% can be written as AV_>_40\n2.SR-Sharpe Ratio\tAV-Annual Volatility\tMDD-Maximum Drawdown\tVaR-Value at Risk\tcVaR-Conditional Value at Risk\tSC-Score\n")
            filters = input(">>> ").split()
            
            use_filter = False


    # Next Baseline
    if prefer == "2":
        print("\nEnter your preferred Index Name\n")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index = indexes[int(input('1.Nifty 50\n2.Bank Nifty\n3.Nasdaq\n4.S&P500\n5.FTSE250\n6.FTSE100\n7.DOW\n8.IBOVESPA\n9.NSE All\n10.NSE Custom\n>>> '))-1]

        obj = MarketScreener(index)
        print(obj.get_baseline_stats())


    # Details Individual Stocks
    if prefer == "3":
        print("\nEnter your preferred Index Name\n")

        indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
        index = indexes[int(input('1.Nifty 50\n2.Bank Nifty\n3.Nasdaq\n4.S&P500\n5.FTSE250\n6.FTSE100\n7.DOW\n8.IBOVESPA\n9.NSE All\n10.NSE Custom\n>>> '))-1]

        obj = MarketScreener(index)
        tick = input("\nEnter Stock Ticker\n>>> ")
        df = obj.individual_details(tick)
        print("\n")
        print(df)


    # Asset Allocation
    if prefer == "4":
        cash = input("\nEnter Cash: ").strip()
        if cash.isnumeric():
            cash = int(cash)
            # Optimisation method check
            print("Select the desired Optimisation Method \n")
            print("1. Max Sharpe")
            print("2. Kelly")
            print("3. HRP")
            print("4. Min Vol")
            print("\n")

            option = input(">>> ")
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
            print("Select the desired Shrinkage Method \n")
            print("1. Ledoit Wolf")
            print("2. Semi-Covariance")
            print("3. Sample Covarinace")
            print("4. Exp. Covariance")
            print("\n")

            option = input(">>> ")
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

            num_stocks = min(int(input("\nEnter the number of unique stocks for portfolio construction (Max. 10): ")), 10)

            stock_names = []
            for i in range(num_stocks):
                print(f"\nEnter Symbol No.{i+1} ")
                stock_names.append(input(">>> ").strip().upper())

            gre_lin = input("\nEnter G for Greedy Portfolio and L for Linear Portfolio:\n>>> ").upper().strip()
            print("\n")
            if gre_lin == "G":
                alloc = "Greedy"
            elif gre_lin == "L":
                alloc = "Linear"

            A, B, C = obj.asset_allocation(cash, stock_names, method, shrinkage, alloc)
            print("\nQuantity of Shares to buy for each ticker\n\n", A)
            print("\n")
            print("Leftover Balance: ", B)
            print("\n")
            print("Weights of Stocks\n\n", C)


    # Correlation Check
    if prefer == "5":
        num_stocks_corr = min(int(input("\nEnter the number of unique stocks for portfolio construction (Max. 10): ")), 10)

        stock_names_corr = []
        for i in range(num_stocks_corr):
            print(f"\nEnter Symbol No.{i+1} ")
            stock_names_corr.append(input(">>> ").strip().upper())

        print("\nThe correlation matrix for the given stocks\n", obj.corr_cals(stock_names_corr))


    # Continue to use the screener
    if prefer == "6":
        print("Exiting...")
        break
