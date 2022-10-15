from screener_investor import MarketScreener

print("="*150)
print("WELCOME TRADERS")
print("="*150)
print("\n\n")


print("Enter your preferred Index Name\n")
indexes = ['NIFTY_50', 'NIFTY_BANK', 'NASDAQ', 'SP500', 'FTSE250', 'FTSE100', 'DOW', 'IBOVESPA', 'NSE', 'NSE Custom']
index = indexes[int(input('1.Nifty 50\n2.Bank Nifty\n3.Nasdaq\n4.S&P500\n5.FTSE250\n6.FTSE100\n7.DOW\n8.IBOVESPA\n9.NSE All\n10.NSE Custom\n>>> '))-1]
obj = MarketScreener(index)

# Driver Code
screen = input("\nInterested in using screener ? Y/N\n>>> ").upper().strip()
if screen == "Y":
    print(obj._index_stocks_stats())

# Next Baseline
base = input("\nInterested to see how the Baseline Index Performed ? Y/N\n>>> ").upper().strip()
if base == "Y":
    print(obj.get_baseline_stats())

# Details Individual Stocks
indi_stock = input("\nInterested in checking the details of a particular stock ? Y/N\n>>> ").upper().strip()
if indi_stock == "Y":
    df = obj.individual_details(input("\nEnter Stock Ticker\n>>> "))
    print("\n")
    print(df)

# Asset Allocation
asset_allocation = input("\nInterested in Asset Allocation ? Y/N\n>>> ").upper().strip()
if asset_allocation == "Y":
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

corr = input("\nInterested in seeing the correlation between stocks ? Y/N\n>>> ").upper().strip()
if corr == "Y":
    num_stocks_corr = min(int(input("\nEnter the number of unique stocks for portfolio construction (Max. 10): ")), 10)

    stock_names_corr = []
    for i in range(num_stocks_corr):
        print(f"\nEnter Symbol No.{i+1} ")
        stock_names_corr.append(input(">>> ").strip().upper())

    print("\nThe correlation matrix for the given stocks\n", obj.corr_cals(stock_names_corr))