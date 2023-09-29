import os
import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler

class CustomLogFilter(logging.Filter):
    """A custom filter class that extends the logging filter to add additional attributes to log records.

    This filter takes any number of keyword arguments and adds them as attributes to log records
    processed by the filter.

    Parameters
    ----------
    **kwargs : dict
        Additional key-value pairs to be added as attributes to log records.

    Examples
    --------
    >>> custom_filter = CustomLogFilter(user="Alice", action="Login")
    >>> logger.addFilter(custom_filter)
    >>> logger.info("User action")
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def filter(self, record):
        """Adds additional attributes to the log record and returns True.

        The additional attributes are specified in the `kwargs` dictionary provided
        during the initialization of the filter.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to which the additional attributes will be added.

        Returns
        -------
        bool
            Always returns True, allowing the log record to be processed by subsequent filters.
        """
        for key, value in self.kwargs.items():
            setattr(record, key, str(value))
        return True

class Logger:
    """Logger class provides a way to log information in different handlers, like stream and file.
    It also has the option to log in Azure App Insight by providing the connection string.

    Parameters
    ----------
    azure_connection_string : str, optional
        Connection string to Azure Application Insights. Defaults to None.
    stream_handler : bool, optional
        If True, adds a stream handler to the logger. Defaults to True.
    file_handler : bool, optional
        If True, adds a file handler to the logger. Defaults to False.
    azure_handler : bool, optional
        If True, adds an Azure handler to the logger. Defaults to False.
    log_lvl : int, optional
        Log level of the handler. Defaults to logging.INFO.
    **kwargs : dict
        Additional key-value pairs to be added as log message attributes.

    Notes
    -----
    Azure App Insights Custom Dimensions
    To add a custom dimensions to all the logRecords and sent it to Azure App Insights:
    Logger should be initialized with arg with the named `custom_dimensions` and a dict[str,str] should be pass to it.

    Returns
    -------
    logging.Logger
        A logging.Logger object to log messages.
    """

    DEFAULT_BASE_FORMAT  = "[%(asctime)s] - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, azure_connection_string=None, stream_handler=True, file_handler=False, azure_handler=False, log_lvl=logging.INFO, **kwargs) -> None:
        self.kwargs = kwargs
        self._stream_handler = stream_handler
        self._file_handler = file_handler
        self.azure_connection_string = azure_connection_string
        self.log_lvl = log_lvl
        self._log_format = self._create_log_format()
        self._azure_handler = azure_handler

    def _create_log_format(self):
        """Creates log format by appending additional key from self.kwargs to the DEFAULT_BASE_FORMAT.
        """
        extra_keys = "".join(f" [%({key})s] -" for key in self.kwargs)
        return self.DEFAULT_BASE_FORMAT[:33] + extra_keys + self.DEFAULT_BASE_FORMAT[33:]

    def _add_lvl_formater(self,handler):
        """Adds log level and formatter to the handler.
        """
        handler.setLevel(self.log_lvl)
        handler.setFormatter(logging.Formatter(self._log_format,datefmt=self.DEFAULT_TIME_FORMAT))
        return handler

    def _add_azure_handler(self):
        """Checks if azure app insight handler should be added or not.
        """
        return (( self.azure_connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") ) and (self._azure_handler))

    def get_file_handler(self):
        """Gets file handler with log level and formatter added.

        Returns
        -------
        logging.FileHandler
            a file handler with level and formatter added.
        """
        file_handler = logging.FileHandler("logs.log")
        return self._add_lvl_formater(file_handler)

    def get_stream_handler(self):
        """Gets stream handler with log level and formatter added.

        Returns
        -------
        logging.StreamHandler
            a stream handler with level and formatter added.
        """
        stream_handler = logging.StreamHandler()
        return self._add_lvl_formater(stream_handler)

    def get_azure_handler(self):
        """Gets stream handler with log level and formatter added.

        Returns
        -------
        AzureLogHandler
            a Azure Log Handler with level and formatter added.
        """
        if self.azure_connection_string is not None:
            azure_handler = AzureLogHandler(connection_string=self.azure_connection_string)
            return self._add_lvl_formater(azure_handler)
        elif os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") is not None:
            azure_handler = AzureLogHandler()
            return self._add_lvl_formater(azure_handler)

    def get_logger(self,name="") -> logging.Logger:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_lvl)
        if self._stream_handler:
            self.logger.addHandler(self.get_stream_handler())
        if self._file_handler:
            self.logger.addHandler(self.get_file_handler())
        if self._add_azure_handler():
            self.logger.addHandler(self.get_azure_handler())
        self.logger.addFilter(CustomLogFilter(**self.kwargs))
        return self.logger