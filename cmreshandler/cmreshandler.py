""" Elasticsearch logging handler
"""

import logging
from enum import Enum
from elasticsearch import helpers as eshelpers
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_kerberos import HTTPKerberosAuth, DISABLED
import datetime
import socket
from threading import Timer


class CMRESHandler(logging.Handler):
    """ Elasticsearch log handler

    Allows to log to elasticsearch into json format.
    All LogRecord fields are serialised and inserted
    """

    class AuthType(Enum):
        """ Authentication types supported

        The handler supports
         - No authentication
         - Basic authentication
         - Kerberos or SSO authentication (on windows and linux)
        """
        NO_AUTH = 0
        BASIC_AUTH = 1
        KERBEROS_AUTH = 2

    # Defauls for the class
    __DEFAULT_HOST = [{'host': 'localhost', 'port': 9200}]
    __DEFAULT_AUTH_USER = ''
    __DEFAULT_AUTH_PASSWD = ''
    __DEFAULT_USE_SSL = False
    __DEFAULT_VERIFY_SSL = True
    __DEFAULT_AUTH_TYPE = AuthType.NO_AUTH
    __DEFAULT_BUFFER_SIZE = 1000
    __DEFAULT_FLUSH_FREQUENCY_IN_SEC = 1
    __DEFAULT_ADDITIONAL_FIELDS = {}
    __DEFAULT_ES_INDEX_NAME = 'python_logger'
    __DEFAULT_ES_DOC_TYPE = 'python_log'
    __DEFAULT_RAISE_ON_INDEXING_EXCEPTIONS = False

    __LOGGING_FILTER_FIELDS = ['msecs',
                               'relativeCreated',
                               'levelno',
                               'created']

    def __init__(self,
                 hosts=__DEFAULT_HOST,
                 auth_details=(__DEFAULT_AUTH_USER, __DEFAULT_AUTH_PASSWD),
                 auth_type=__DEFAULT_AUTH_TYPE,
                 use_ssl=__DEFAULT_USE_SSL,
                 verify_ssl=__DEFAULT_VERIFY_SSL,
                 buffer_size=__DEFAULT_BUFFER_SIZE,
                 flush_frequency_in_sec=__DEFAULT_FLUSH_FREQUENCY_IN_SEC,
                 es_index_name=__DEFAULT_ES_INDEX_NAME,
                 es_doc_type=__DEFAULT_ES_DOC_TYPE,
                 es_additional_fields=__DEFAULT_ADDITIONAL_FIELDS,
                 raise_on_indexing_exceptions=__DEFAULT_RAISE_ON_INDEXING_EXCEPTIONS):
        """ Handler constructor

        :param hosts: The list of hosts that elasticsearch clients will connect. The list can be provided
                    in the format ```[{'host':'host1','port':9200}, {'host':'host2','port':9200}]``` to
                    make sure the client supports failover of one of the instertion nodes
        :param auth_details: When ```CMRESHandler.AuthType.BASIC_AUTH``` is used this argument must contain
                    a tuple of string with the user and password that will be used to authenticate against
                    the Elasticsearch servers, for example```('User','Password')
        :param auth_type: The authentication type to be used in the connection ```CMRESHandler.AuthType```
                    Currently, NO_AUTH, BASIC_AUTH, KERBEROS_AUTH are supported
        :param use_ssl: A boolean that defines if the communications should use SSL encrypted communication
        :param verify_ssl: A boolean that defines if the SSL certificates are validated or not
        :param buffer_size: An int, Once this size is reached on the internal buffer results are flushed into ES
        :param flush_frequency_in_sec: A float representing how often and when the buffer will be flushed, even
                    if the buffer_size has not been reached yet
        :param es_index_name: A string with the prefix of the elasticsearch index that will be created. Note a
                    date with YYYY.MM.dd, ```python_logger``` used by default
        :param es_doc_type: A string with the name of the document type that will be used ```python_log``` used
                    by default
        :param es_additional_fields: A dictionary with all the additional fields that you would like to add
                    to the logs, such the application, environment, etc.
        :param raise_on_indexing_exceptions: A boolean, True only for debugging purposes to raise exceptions
                    caused when
        :return: A ready to be used CMRESHandler.
        """
        logging.Handler.__init__(self)

        self.hosts = hosts
        self.auth_details = auth_details,
        self.auth_type = auth_type
        self.use_ssl = use_ssl
        self.verify_certs = verify_ssl
        self.buffer_size = buffer_size
        self.flush_frequency_in_sec = flush_frequency_in_sec
        self.es_index_name = es_index_name
        self.es_doc_type = es_doc_type
        self.es_additional_fileds = es_additional_fields.copy()
        self.es_additional_fileds.update({'host': socket.gethostname(),
                                          'host_ip': socket.gethostbyname(socket.gethostname())})
        self.raise_on_indexing_exceptions = raise_on_indexing_exceptions

        self._buffer = []
        self._timer = None
        self.__schedule_flush()

    def __schedule_flush(self):
        if self._timer is None:
            self._timer = Timer(self.flush_frequency_in_sec, self.flush)
            self._timer.setDaemon(True)
            self._timer.start()

    def __get_es_client(self):
        if self.auth_type == CMRESHandler.AuthType.NO_AUTH:
            return Elasticsearch(hosts=self.hosts,
                                 use_ssl=self.use_ssl,
                                 verify_certs=self.verify_certs,
                                 connection_class=RequestsHttpConnection)
        elif self.auth_type == CMRESHandler.AuthType.BASIC_AUTH:
            return Elasticsearch(hosts=self.hosts,
                                 http_auth=self.auth_details,
                                 use_ssl=self.use_ssl,
                                 verify_certs=self.verify_certs,
                                 connection_class=RequestsHttpConnection)
        elif self.auth_type == CMRESHandler.AuthType.KERBEROS_AUTH:
            return Elasticsearch(hosts=self.hosts,
                                 use_ssl=self.use_ssl,
                                 verify_certs=self.verify_certs,
                                 connection_class=RequestsHttpConnection,
                                 http_auth=HTTPKerberosAuth(mutual_authentication=DISABLED))

    def test_es_source(self):
        """ Returns True if the handler can ping the Elasticsearch servers

        Can be used to confirm the setup of a handler has been properly done and confirm
        that things like the authentication is working properly

        :return: A boolean, True if the connection against elasticserach host was successful
        """
        return self.__get_es_client().ping()

    def __get_es_index_name(self):
        """ Returns elasticearch index name
        :return: A srting containing the elasticsearch indexname used which should include the date.
        """
        return "{0!s}-{1!s}".format(self.es_index_name, datetime.datetime.now().strftime('%Y.%m.%d'))

    @staticmethod
    def __get_es_datetime_str(timestamp):
        """ Returns elasticsearch utc formatted time for an epoch timestamp

        :param timestamp: epoch, including milliseconds
        :return: A string valid for elasticsearch time record
        """
        t = datetime.datetime.utcfromtimestamp(timestamp)
        return "{0!s}.{1:03d}Z".format(t.strftime('%Y-%m-%dT%H:%M:%S'), int(t.microsecond / 1000))

    def flush(self):
        """ Flushes the buffer into ES
        :return: None
        """
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None

        # FIXME: This should probably go on a different thread to speed up the execution
        if len(self._buffer) >= 0:
            try:
                actions = map(lambda x: {'_index': self.__get_es_index_name(),
                                         '_type': self.es_doc_type,
                                         '_source': x},
                              self._buffer)
                eshelpers.bulk(client=self.__get_es_client(),
                               actions=actions,
                               stats_only=True)
            except Exception as e:
                if self.raise_on_indexing_exceptions:
                    raise e
            self._buffer = []

        self.__schedule_flush()

    def close(self):
        """ Flushes the buffer and release any outstanding resource

        :return: None
        """
        self.flush()
        self._timer.cancel()
        self._timer = None

    def emit(self, record):
        """ Emit overrides the abstract logging.Handler logRecord emit method

        records the log

        :param record: A class of type ```logging.LogRecord```
        :return: None
        """
        rec = self.es_additional_fileds.copy()
        for k, v in record.__dict__.items():
            if k not in CMRESHandler.__LOGGING_FILTER_FIELDS:
                rec[k] = "" if v is None else v
        rec['timestamp'] = self.__get_es_datetime_str(record.created)

        self._buffer.append(rec)
        if len(self._buffer) >= self.buffer_size:
            self.flush()
