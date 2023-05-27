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


def displayDf(df:DataFrame) -> None:
    # Show Rich Tables
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    viewTable = df_to_table(df, table)
    table.box = box.HEAVY

    print("\n")

    console.print(viewTable)


def displayString(text:str, style="") -> Prompt:
    # Render Text
    promp = Prompt.ask(f"[{style}]{text}[/]")
    return promp


def rules(text:str) -> None:
    # Divide
    print("\n")
    console = Console()
    console.rule(f"[bold red]{text}")


def panelShow(text:str, style="", aligns="center") -> None:
    # Render Panel
    print("\n")

    console = Console()
    console.print(Align(Panel.fit(f"[{style}]{text}[/]"), align=f"{aligns}"))