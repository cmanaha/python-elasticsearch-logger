""" Elasticsearch logging formatter
"""

import logging


class CMRESFormatter(logging.Formatter):
    """ Elasticsearch log formatter

    Allows to format log for a elasticsearch use.
    Some LogRecord fields are formatted.
    """

    def format(self, record):
        """ Format the exc_info to prevent an elasticsearch problem. 

        Use the inherited 'formatException' formatter method 
        to format exc_text containing the stacktrace.
        :param record: A class of type ```logging.LogRecord```
        :return: None
        """
        if record.exc_info:
          if not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
          record.exc_info = str(record.exc_info)
