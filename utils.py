from datetime import datetime
from typing import Optional

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table

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

    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column))

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table


def filter_database(temp:pd.DataFrame, filters:list) -> pd.DataFrame:
    """
    Filters Dataframe based on given filtering criteria
    """
    
    # filtering temp dataframe
    for filt in filters:
        facts = filt.split("_")

        # check for annual volatility condition
        if facts[0]=="AV":
            if facts[1]==">":
                temp = temp[temp['Annual Volatility']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Annual Volatility']<float(facts[2])]
            else:
                temp = temp[temp['Annual Volatility']==float(facts[2])]

        # check for sharpe ratio
        elif facts[0]=="SR":
            if facts[1]==">":
                temp = temp[temp['Sharpe Ratio']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Sharpe Ratio']<float(facts[2])]
            else:
                temp = temp[temp['Sharpe Ratio']==float(facts[2])]

        # check for max drawdown
        elif facts[0]=="MDD":
            if facts[1]==">":
                temp = temp[temp['MaxDD']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['MaxDD']<float(facts[2])]
            else:
                temp = temp[temp['MaxDD']==float(facts[2])]

        # check for conditional VaR
        elif facts[0]=="cVaR":
            if facts[1]==">":
                temp = temp[temp['CVaR']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['CVaR']<float(facts[2])]
            else:
                temp = temp[temp['CVaR']==float(facts[2])]

        # check for VaR
        elif facts[0]=="VaR":
            if facts[1]==">":
                temp = temp[temp['VaR']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['VaR']<float(facts[2])]
            else:
                temp = temp[temp['VaR']==float(facts[2])]

        # check for PER
        elif facts[0]=="PER":
            if facts[1]==">":
                temp = temp[temp['PE Ratio']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['PE Ratio']<float(facts[2])]
            else:
                temp = temp[temp['PE Ratio']==float(facts[2])]

        # check for Dividend
        elif facts[0]=="DVD":
            if facts[1]==">":
                temp = temp[temp['Dividend']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Dividend']<float(facts[2])]
            else:
                temp = temp[temp['Dividend']==float(facts[2])]

        # check for score
        else:
            if facts[1]==">":
                temp = temp[temp['Score']>float(facts[2])]
            elif facts[1]=="<":
                temp = temp[temp['Score']<float(facts[2])]
            else:
                temp = temp[temp['Score']==float(facts[2])]

    return temp

