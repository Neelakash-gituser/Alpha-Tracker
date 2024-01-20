# Imports
from logger._logger import logger, get_exception_line_no
from datetime import datetime

logger_backtset_strategy = logger.getLogger("backtest_strategy")


class Strategy:

    def __init__(self, start_date:datetime, end_date:datetime, signal, securities:list) -> None:
        # assign start date and end date
        self.start_date = start_date
        self.end_date = end_date

        # get the signal for trading
        self.signal = signal

        # trading securities
        self.securities = securities

    def run(self):
        pass

    