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

        Use the inherited formatter to format asctime and exc_text.
        :param record: A class of type ```logging.LogRecord```
        :return: None
        """
        super(CMRESFormatter, self).format(record)
        record.exc_info = str(record.exc_info)
