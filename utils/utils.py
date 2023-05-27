import pandas as pd

from rich import box
from typing import Optional
from rich.table import Table
from datetime import datetime
from rich.console import Console


# Dataframe styling 
def df_to_table(
    pandas_dataframe: pd.DataFrame,
    rich_table: Table,
    show_index: bool = True,
    index_name: Optional[str] = None,
) -> Table:
    
    """Convert a pandas.DataFrame obj into a rich.Table obj.
    Args:
        pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
        show_index (bool): Add a column with a row count to the table. Defaults to True.
        index_name (str, optional): The column name to give to the index column. Defaults to None, showing no value.
    Returns:
        Table: The rich Table instance passed, populated with the DataFrame values."""

    colors, hashKey = ["cyan", "magenta", "green"], 0

    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column), justify="right", style=colors[hashKey%len(colors)])

    for index, value_list in zip(pandas_dataframe.index.to_list(), pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table


# Database filtering and screening
def filter_database(_temp:pd.DataFrame, filters:list) -> pd.DataFrame:
    """
    Filters Dataframe based on given filtering criteria
    """
    temp = _temp.copy()

    # filtering temp dataframe
    for filt in filters:
        facts = filt.split("_")

        # check for annual volatility condition
        if facts[0].upper() == "AV":
            if facts[1]==">":
                temp = temp[temp['Annual Volatility']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Annual Volatility']<float(facts[2])]
            else:
                temp = temp[temp['Annual Volatility']==float(facts[2])]

        # check for sharpe ratio
        elif facts[0].upper() == "SR":
            if facts[1]==">":
                temp = temp[temp['Sharpe Ratio']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Sharpe Ratio']<float(facts[2])]
            else:
                temp = temp[temp['Sharpe Ratio']==float(facts[2])]

        # check for max drawdown
        elif facts[0].upper() == "MDD":
            if facts[1]==">":
                temp = temp[temp['Maximum Drawdown']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Maximum Drawdown']<float(facts[2])]
            else:
                temp = temp[temp['Maximum Drawdown']==float(facts[2])]

        # check for conditional VaR
        elif facts[0].upper() == "cVaR":
            if facts[1]==">":
                temp = temp[temp['cVaR']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['cVaR']<float(facts[2])]
            else:
                temp = temp[temp['cVaR']==float(facts[2])]

        # check for VaR
        elif facts[0].upper() == "VaR":
            if facts[1]==">":
                temp = temp[temp['VaR']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['VaR']<float(facts[2])]
            else:
                temp = temp[temp['VaR']==float(facts[2])]

        # check for Annual Return
        elif facts[0].upper() == "AR":
            if facts[1]==">":
                temp = temp[temp['Annual Return']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Annual Return']<float(facts[2])]
            else:
                temp = temp[temp['Annual Return']==float(facts[2])]

        # check for Highest Peak
        elif facts[0].upper() == "HP":
            if facts[1]==">":
                temp = temp[temp['Highest Peak']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Highest Peak']<float(facts[2])]
            else:
                temp = temp[temp['Highest Peak']==float(facts[2])]

        # check for Lowest Trough
        elif facts[0].upper() == "LT":
            if facts[1]==">":
                temp = temp[temp['Lowest Trough']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Lowest Trough']<float(facts[2])]
            else:
                temp = temp[temp['Lowest Trough']==float(facts[2])]

        # check for Current Price
        elif facts[0].upper() == "CP":
            if facts[1]==">":
                temp = temp[temp['Current Price']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Current Price']<float(facts[2])]
            else:
                temp = temp[temp['Current Price']==float(facts[2])]


    return temp


def check_market(index:str) -> bool:
    """
    True if Indian Market else False
    """
    return index in ['NIFTY_50', 'NIFTY_BANK', 'NSE'] 


def make_ticker_nse(tickers:list) -> list:
    """
    Returns NSE ticker with .NS in the suffix.
    """
    return pd.Series(tickers).apply(lambda x: x + ".NS" if x[-3:]!=".NS" else x).to_list()

