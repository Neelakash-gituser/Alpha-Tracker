from rich import box
from rich.style import Style
from rich.layout import Layout
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt
from rich.markdown import Markdown, Heading

from pandas import DataFrame
from utils.utils import df_to_table


def displayDf(df: DataFrame) -> None:
    """
    Display a Pandas DataFrame as a rich table.

    This function takes a Pandas DataFrame and displays it as a rich table using the Rich library.

    :param df: The DataFrame to display.
    :type df: DataFrame

    :return: None
    """
    # Show Rich Tables
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    viewTable = df_to_table(df, table)
    table.box = box.HEAVY

    print("\n")

    console.print(viewTable)


def displayString(text: str, style="") -> Prompt:
    """
    Display a formatted string using Rich and return user input as a Prompt.

    This function displays a formatted string using the Rich library and returns user input as a Prompt.

    :param text: The text to display.
    :type text: str

    :param style: The style to apply to the text (e.g., "bold red").
    :type style: str, optional

    :return: A user input Prompt.
    :rtype: Prompt
    """
    # Render Text
    promp = Prompt.ask(f"[{style}]{text}[/]")
    return promp


def rules(text: str) -> None:
    """
    Display a divider rule with a specified text.

    This function displays a divider rule with a specified text using the Rich library.

    :param text: The text to display.
    :type text: str

    :return: None
    """
    # Divide
    print("\n")
    console = Console()
    console.rule(f"[bold red]{text}")


def panelShow(text: str, style="", aligns="center") -> None:
    """
    Display a text panel with specified style and alignment.

    This function displays a text panel with specified style and alignment using the Rich library.

    :param text: The text to display in the panel.
    :type text: str

    :param style: The style to apply to the text (e.g., "bold").
    :type style: str, optional

    :param aligns: The alignment for the panel (e.g., "center").
    :type aligns: str, optional

    :return: None
    """
    # Render Panel
    print("\n")

    console = Console()
    console.print(Align(Panel.fit(f"[{style}]{text}[/]"), align=f"{aligns}"))
