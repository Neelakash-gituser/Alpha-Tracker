
import os
import sys
from datetime import datetime
import logging as logger

from utils.global_variables import LOG_FILE_PATH


def get_exception_line_no():
    """
    Get the line number where the current exception was raised.

    This function retrieves the line number from the exception traceback
    to determine the line where the current exception was raised.

    :return: The line number where the exception was raised.
    :rtype: int
    """
    _, _, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    return line_number



def change_log_file_handler(val=""):
    """
    Change the log file handler for the application's logger.

    This function creates a new log file with a timestamp and an optional value suffix
    for the application's logger. It updates the logger's handlers to use the new log file.

    :param val: An optional suffix to include in the log file name.
    :type val: str, optional

    :return: None
    """
    dt_now = datetime.now().strftime('%Y%m%d%H%M%S%f')
    
    if val != '':
        LOG_FILE = f"stock_app_{dt_now}_{val}.log"
    else:
        LOG_FILE = f"stock_app_{dt_now}.log"
    
    os.makedirs(LOG_FILE_PATH, exist_ok= True)

    logs_path = os.path.join(LOG_FILE_PATH,LOG_FILE)

    file_handler = logger.FileHandler(logs_path)
    formatter = logger.Formatter("[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.getLogger().addHandler(file_handler)

    for handler in logger.getLogger().handlers:
        logger.getLogger().removeHandler(handler)

    file_handler.close()


def init_logger():
    """
    Initialize and configure a logger for the application.

    This function creates and configures a logger for the application. It sets up the logger
    to write log messages to a file with a timestamped name in the specified log directory.

    :return: A logger instance configured for the application.
    :rtype: logger.Logger
    """
    dt_now = datetime.now().strftime('%Y%m%d%H%M%S%f')
    LOG_FILE = f"stock_app_{dt_now}.log"

    logs_path = os.path.join(LOG_FILE_PATH, LOG_FILE)

    # # TODO: need to change the output file when gets bigger
    os.makedirs(LOG_FILE_PATH, exist_ok= True)

    logger.basicConfig(
        filename=logs_path,
        format = "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    )

    if True:
        logger.getLogger().setLevel(logger.INFO)

    return logger


# invoke the logger
logger = init_logger()
