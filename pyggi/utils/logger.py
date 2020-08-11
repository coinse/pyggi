"""

This module contains Logger class.

"""
import os
import pathlib
import logging
from .. import PYGGI_DIR

class Logger(object):
    """
    Logger class is used to records execution information.
    It wraps the Logger object from logging module which
    have two handlers: file handler and stream handler.
    5 logging levels are available: debug, info, warning, error, critial.
    For more information, see https://docs.python.org/3.6/library/logging.html .
    """
    LOG_DIR = os.path.join(PYGGI_DIR, 'logs')

    def __init__(self, name):
        import time
        import os
        # initialize
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s')
        # log directory
        if not os.path.exists(Logger.LOG_DIR):
            pathlib.Path(Logger.LOG_DIR).mkdir(parents=True)
        # file handler
        self.log_file_path = os.path.join(Logger.LOG_DIR, "{}.log".format(name))
        file_handler = logging.FileHandler(self.log_file_path, delay=True)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        # stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        # add handlers to the logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(stream_handler)

    def debug(self, msg, *args, **kwargs):
        """
        Logs a message with level DEBUG on this logger

        :param msg: The message to record
        :return: None
        """
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Logs a message with level INFO on this logger

        :param msg: The message to record
        :return: None
        """
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Logs a message with level WARNING on this logger

        :param msg: The message to record
        :return: None
        """
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Logs a message with level ERROR on this logger

        :param msg: The message to record
        :return: None
        """
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Logs a message with level CRITICAL on this logger

        :param msg: The message to record
        :return: None
        """
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)
