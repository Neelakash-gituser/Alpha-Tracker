import os
import talib as ta
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import plotly.graph_objects as go

from tqdm import tqdm
from numpy.linalg import inv
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier
from pypfopt import objective_functions
from pypfopt.risk_models import risk_matrix
from pypfopt.hierarchical_portfolio import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from yahoo_fin import stock_info as sf
from cloudcraftz.utils import drawdown
from cloudcraftz.statistical_tests import var_historic, cvar_historic



class MarketScreener:

    # Constructor
    def __init__(self, indexes, lookback=365, topn=0.01):
        self.start = dt.datetime.now() - dt.timedelta(days=lookback)
        self.end = dt.datetime.now()
        self.indexes = indexes
        self.MA = ['SMA_50', 'SMA_20']
        self.lookback = lookback
        self.topn = topn

        try:
            os.mkdir('./data')
        except:
            pass

        self._select_index(self.indexes)



    def _select_index(self, index):
        # Selects Index

        if index == 'NIFTY_50':
            tickers = sf.tickers_nifty50()
            tickers.remove("MM.NS")
            baseline = yf.download(tickers='^NSEI', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'NIFTY_BANK':
            tickers = sf.tickers_niftybank()
            tickers = pd.Series(tickers).apply(lambda x: x + '.NS').to_list()
            baseline = yf.download(tickers='^NSEBANK', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'NASDAQ':
            tickers = sf.tickers_nasdaq()
            baseline = yf.download(tickers='^IXIC', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'SP500':
            tickers = sf.tickers_sp500()
            baseline = yf.download(tickers='^GSPC', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'FTSE250':
            tickers = sf.tickers_ftse250()
            baseline = yf.download(tickers='^FTMC', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'FTSE100':
            tickers = sf.tickers_ftse100()
            baseline = yf.download(tickers='^FTSE', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'DOW':
            tickers = sf.tickers_dow()
            baseline = yf.download(tickers='^DJI', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'IBOVESPA':
            tickers = sf.tickers_ibovespa()
            baseline = yf.download(tickers='^BVSP', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'NSE':
            tickers = []
            url = pd.read_csv('./ind_nifty100list.csv')['Symbol']

            tickers = list(url.apply(lambda x: x.strip() +'.NS').unique())

            baseline = yf.download(tickers='^NSEI', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        elif index == 'NSE Custom':
            tickers = []
            for i in range(100):
                try:
                    j = input('Enter ticker name: ').upper().strip() + '.NS'
                    tickers.append(j)
                    print("Add more tickers ?")
                    ans = input('Y/N: ').upper().strip()

                    if ans == 'N':
                        break
                except:
                    pass

            baseline = yf.download(tickers='^NSEI', start=self.start, end=self.end, progress=False)
            self.tickers = tickers

        self.baseline = baseline


    # Baseline information
    def _baseline_stats(self):
        self.baseline['returns'] = self.baseline['Adj Close'].pct_change()
        baseline_returns = (1+self.baseline['returns']).cumprod()[-1]

        vola = np.std(self.baseline['Adj Close'].pct_change()) * np.sqrt(252)
        sharpe = (((baseline_returns-1) / self.lookback) * (252)) / vola
        max_dd = drawdown(self.baseline['Adj Close'].pct_change())['Drawdown'].min()

        sma_20 = ta.SMA(self.baseline['Adj Close'], timeperiod=20).values[-1]
        sma_50 = ta.SMA(self.baseline['Adj Close'], timeperiod=50).values[-1]
        var = var_historic(self.baseline['Adj Close'].pct_change().dropna())
        cvar = cvar_historic(self.baseline['Adj Close'].pct_change().dropna())


        return baseline_returns, vola, sharpe, max_dd, sma_20, sma_50, cvar, var


    # Info of all stocks in the index
    def _index_stocks_stats(self):
        return_list = []
        weeks = (self.lookback / 365) * 52
        final_df = pd.DataFrame(columns=['TIC', 'Latest Price', 'Score', 'PE Ratio', 'Dividend', 'SMA_20', 'SMA_50', f'{int(weeks)}_Week_Low',
                                        f'{int(weeks)}_Week_High',
                                        'Annual Volatility', 'Sharpe Ratio', 'MaxDD', 'CVaR', 'VaR'])

        for i in tqdm(self.tickers):
            try:
                data = yf.download(tickers=i, start=self.start, end=self.end, progress=False)
                data.to_csv('data/'+i+'.csv')
                data['returns'] = data['Adj Close'].pct_change()
                rets = (1+data['returns']).cumprod()[-1]
                return_list.append(round((rets/self._baseline_stats()[0]), 2))
            except Exception as e:
                pass

        df = pd.DataFrame(list(zip(self.tickers, return_list)), columns=['TIC', 'Returns Relative to Index'])

        # Assigning a score based on ratio of - return of stock / return of index
        df['Score'] = df['Returns Relative to Index'].rank(pct=True) * 100
        df = df[df['Score'] >= df['Score'].quantile(self.topn)]

        for i in tqdm(df['TIC']):
            try:
                # new_df = yf.download(tickers=i, start=self.start, end=self.end, progress=False)
                new_df = pd.read_csv('data/'+i+'.csv', index_col=0)
                for mvs in self.MA:
                    new_df[mvs] = ta.SMA(new_df['Adj Close'], timeperiod=int(mvs[-2:]))

                # Calculating various parameters such as sharpe ratio, volatility etc.
                latest_price = new_df['Adj Close'][-1]
                pe_ratio = float(sf.get_quote_table(i)['PE Ratio (TTM)'])
                peg_ratio = float(sf.get_dividends(i)['dividend'][-1])
                mov_20 = new_df['SMA_20'][-1]
                mov_50 = new_df['SMA_50'][-1]
                lows = round(min(new_df['Low'][(-int(weeks)*5):]), 2)
                highs = round(max(new_df['High'][(-int(weeks)*5):]), 2)
                scores = round(df[df['TIC'] == i]['Score'].to_list()[0])
                vola = np.std(new_df['Adj Close'].pct_change()) * np.sqrt(252)
                sharpe = round((((((1+new_df['Adj Close'].pct_change()).cumprod()[-1] - 1) / (self.lookback)) * 252) / vola), 2)
                maxdd = drawdown(new_df['Adj Close'].pct_change())['Drawdown'].min()
                cvar = cvar_historic(new_df['Adj Close'].pct_change().dropna())
                var = var_historic(new_df['Adj Close'].pct_change().dropna())

                # Always True
                if True:
                    final_df = final_df.append({
                         'TIC': i,
                         'Latest Price': latest_price,
                         'Score': scores,
                         'PE Ratio': pe_ratio,
                         'Dividend': peg_ratio,
                         'SMA_20': mov_20,
                         'SMA_50': mov_50,
                         f'{int(weeks)}_Week_Low': lows,
                         f'{int(weeks)}_Week_High': highs,
                         'Annual Volatility': vola,
                         'Sharpe Ratio': sharpe,
                         'MaxDD': maxdd,
                         'CVaR': cvar,
                         'VaR': var
                    }, ignore_index=True)

            except Exception as e:
                pass

        final = final_df.sort_values(by="Score", ascending=False)
        final.reset_index(inplace=True, drop=True)

        return final


    # Allocation of various stocks.
    def asset_allocation(self, cash, ticker_list, opt_method, use_method="ledoit_wolf", alloc="Linear", freq="M"):
        df = pd.DataFrame()

        for i in ticker_list:
            try:
                data = pd.read_csv('data/'+i+'.csv', index_col=0)
            except:
                data = yf.download(i, start=self.start, end=self.end, progress=False)

            data['TIC'] = i
            df = df.append(data)

        df.index = pd.to_datetime(df.index)
        df = df[['TIC', 'Adj Close']].reset_index().set_index(['Date', 'TIC']).unstack()
        df.columns = df.columns.droplevel(0)
        df.columns.name = None
        df_cov = df.copy()

        if freq == "M":
            freq = 12
            df = df.resample("M").last()
            df = df.reset_index()
            df['Date'] = df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
            df.set_index("Date", inplace=True)

        elif freq == "D":
            freq = 252
            df = df.reset_index()
            df['Date'] = df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
            df.set_index("Date", inplace=True)

        # Historical returns
        retu = expected_returns.mean_historical_return(df, frequency=freq)

        returns = retu
        mean_returns = returns
        cov = risk_matrix(df_cov, method=use_method)
        precision_matrix = pd.DataFrame(inv(cov), index=ticker_list, columns=ticker_list)  # Inverse of cov matrix


        if (opt_method.lower()=="max_sharpe"):

            ef = EfficientFrontier(retu, cov)
            weights = ef.nonconvex_objective(
            objective_functions.sharpe_ratio,
            objective_args = (ef.expected_returns, ef.cov_matrix),
            weights_sum_to_one=True,
            )

            print(ef.portfolio_performance(verbose=True))

            wts = weights
            weights = wts

        elif (opt_method.lower()=="min_vol"):

            ef = EfficientFrontier(retu, cov, verbose=False)
            ef.add_objective(objective_functions.L2_reg, gamma=1)

            ef.min_volatility()
            wts = ef.clean_weights()

            print(ef.portfolio_performance(verbose=True))
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
        latest_prices = get_latest_prices(df)
        da = DiscreteAllocation(weights, latest_prices, cash)

        if alloc == "Linear":
            allocation, leftover = da.lp_portfolio()
        else:
            allocation, leftover = da.greedy_portfolio()

        tf = pd.DataFrame(allocation, index=['No. of Shares'])

        # Save all information
        new_final_df = pd.concat([tf.T, pd.DataFrame(weights, index=['Weights']).T], axis=1)
        new_final_df.to_excel("Allocations.xlsx")

        return new_final_df


    # Correlation Calculator
    def corr_cals(self, ticker_list):
        df = pd.DataFrame()

        for i in ticker_list:
            try:
                data = pd.read_csv('data/'+i+'.csv', index_col=0)
            except:
                data = yf.download(i, start=self.start, end=self.end, progress=False)

            data['TIC'] = i
            df = df.append(data)

        df = df[['TIC', 'Adj Close']].reset_index().set_index(['Date', 'TIC']).unstack()
        df.columns = df.columns.droplevel(0)
        df.columns.name = None

        df.corr().to_excel("Correlation.xlsx")

        return df.corr()

    # More info on individual stocks
    def individual_details(self, stock_name):
        try:
            new_df = pd.read_csv('data/'+stock_name+'.csv', index_col=0)
        except:
            new_df = yf.download(stock_name, self.start, self.end, progress=False)

        df = pd.DataFrame()
        weeks = (self.lookback / 365) * 52
        new_df['SMA_20'] = ta.SMA(new_df['Adj Close'], timeperiod=20)
        new_df['SMA_50'] = ta.SMA(new_df['Adj Close'], timeperiod=50)

        latest_price = new_df['Adj Close'].values[-1]
        pe_ratio = float(sf.get_quote_table(stock_name)['PE Ratio (TTM)'])
        peg_ratio = float(sf.get_dividends(stock_name)['dividend'][-1])
        mov_20 = new_df['SMA_20'][-1]
        mov_50 = new_df['SMA_50'][-1]
        lows = round(min(new_df['Low'][(-int(weeks)*5):]), 2)
        highs = round(min(new_df['High'][(-int(weeks)*5):]), 2)
        vola = np.std(new_df['Adj Close'].pct_change()) * np.sqrt(252)
        sharpe = round((((((1+new_df['Adj Close'].pct_change()).cumprod()[-1] - 1) / (self.lookback)) * 252) / vola), 2)
        maxdd = drawdown(new_df['Adj Close'].pct_change())['Drawdown'].min()
        cvar = cvar_historic(new_df['Adj Close'].pct_change().dropna())
        var = var_historic(new_df['Adj Close'].pct_change().dropna())

        EMA_t1 = ta.EMA(new_df['Adj Close'], timeperiod=20)
        EMA_t2 = ta.EMA(new_df['Adj Close'], timeperiod=30)


        SMA_t1 = ta.SMA(new_df['Adj Close'], timeperiod=20)
        SMA_t2 = ta.SMA(new_df['Adj Close'], timeperiod=30)

        df = df.append(pd.DataFrame({
                         'TIC': stock_name,
                         'Latest Price': latest_price,
                         'PE Ratio': pe_ratio,
                         'Dividend': peg_ratio,
                         'SMA_20': mov_20,
                         'SMA_50': mov_50,
                         f'{int(weeks)}_Week_Low': lows,
                         f'{int(weeks)}_Week_High': highs,
                         'Annual Volatility': vola,
                         'Sharpe Ratio': sharpe,
                         'MaxDD': maxdd,
                         'CVaR': cvar,
                         'VaR': var
                    }, index=[0]), ignore_index=True)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = new_df.index,
            y = new_df['Adj Close'],
            name = "Actual Price Movement"
        ))


        fig.add_trace(go.Scatter(
            x = new_df.index,
            y = EMA_t1,
            name = "EMA Short"
        ))

        fig.add_trace(go.Scatter(
            x = new_df.index,
            y = EMA_t2,
            name = "EMA Long"
        ))

        fig.add_trace(go.Scatter(
            x = new_df.index,
            y = SMA_t2,
            name = "SMA Long"
        ))

        fig.add_trace(go.Scatter(
            x = new_df.index,
            y = SMA_t1,
            name = "SMA Short"
        ))

        fig.update_layout(xaxis_title='Dates', yaxis_title='Price')

        fig.show()

        return df

    # Just a function to aggregate our results.
    def get_baseline_stats(self):
        baseline_ret, vola, sharpe, max_dd, sma_20, sma_50, cvar, var = self._baseline_stats()

        return pd.DataFrame([
                             self.start.strftime("%Y-%m-%d"),
                             self.end.strftime("%Y-%m-%d"),
                             sma_20,
                             sma_50,
                             cvar,
                             var,
                             sharpe,
                             vola,
                             baseline_ret,
                             max_dd
                             ], index=['Start Date', 'End Date', 'SMA 20', 'SMA 50', 'CVaR', 'VaR', 'Sharpe Ratio', 'Annual Volatility', 'Cumulative Return', 'Maximum Drawdown'], columns=['Summary'])
