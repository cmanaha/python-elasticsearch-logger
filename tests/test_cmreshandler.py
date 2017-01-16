import unittest
import logging
import time
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from cmreslogging.handlers import CMRESHandler


class CMRESHandlerTestCase(unittest.TestCase):
    DEFAULT_ES_SERVER = 'localhost'
    DEFAULT_ES_PORT = 9200

    def getESHost(self):
        return os.getenv('TEST_ES_SERVER',CMRESHandlerTestCase.DEFAULT_ES_SERVER)

    def getESPort(self):
        try:
            return int(os.getenv('TEST_ES_PORT',CMRESHandlerTestCase.DEFAULT_ES_PORT))
        except ValueError:
            return CMRESHandlerTestCase.DEFAULT_ES_PORT

    def setUp(self):
        self.log = logging.getLogger("MyTestCase")
        test_handler = logging.StreamHandler(stream=sys.stderr)
        self.log.addHandler(test_handler)

    def tearDown(self):
        del self.log

    def test_ping(self):
        handler = CMRESHandler(hosts=[{'host': self.getESHost(), 'port': self.getESPort()}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="pythontest",
                               use_ssl=False)
        es_test_server_is_up = handler.test_es_source()
        self.assertEquals(True, es_test_server_is_up)

    def test_buffered_log_insertion_flushed_when_buffer_full(self):
        handler = CMRESHandler(hosts=[{'host': self.getESHost(), 'port': self.getESPort()}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               buffer_size=2,
                               flush_frequency_in_sec=1000,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  {0!s}".format(es_test_server_is_up))
        self.assertEquals(True, es_test_server_is_up)

        log = logging.getLogger("PythonTest")
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        log.warning("First Message")
        log.info("Seccond Message")
        self.assertEquals(0, len(handler._buffer))
        handler.close()

    def test_es_log_extra_argument_insertion(self):
        self.log.info("About to test elasticsearch insertion")
        handler = CMRESHandler(hosts=[{'host': self.getESHost(), 'port': self.getESPort()}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  {0!s}".format(es_test_server_is_up))
        self.assertEquals(True, es_test_server_is_up)

        log = logging.getLogger("PythonTest")
        log.addHandler(handler)
        log.warning("Extra arguments Message", extra={"Arg1": 300, "Arg2": 400})
        self.assertEquals(1, len(handler._buffer))
        self.assertEquals(handler._buffer[0]['Arg1'], 300)
        self.assertEquals(handler._buffer[0]['Arg2'], 400)
        self.assertEquals(handler._buffer[0]['App'], 'Test')
        self.assertEquals(handler._buffer[0]['Environment'], 'Dev')
        handler.flush()
        self.assertEquals(0, len(handler._buffer))

    def test_buffered_log_insertion_after_interval_expired(self):
        handler = CMRESHandler(hosts=[{'host': self.getESHost(), 'port': self.getESPort()}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               flush_frequency_in_sec=0.1,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  {0!s}".format(es_test_server_is_up))
        self.assertEquals(True, es_test_server_is_up)

        log = logging.getLogger("PythonTest")
        log.addHandler(handler)
        log.warning("Extra arguments Message", extra={"Arg1": 300, "Arg2": 400})
        self.assertEquals(1, len(handler._buffer))
        self.assertEquals(handler._buffer[0]['Arg1'], 300)
        self.assertEquals(handler._buffer[0]['Arg2'], 400)
        self.assertEquals(handler._buffer[0]['App'], 'Test')
        self.assertEquals(handler._buffer[0]['Environment'], 'Dev')
        time.sleep(1)
        self.assertEquals(0, len(handler._buffer))

    def test_fast_insertion_of_hundred_logs(self):
        handler = CMRESHandler(hosts=[{'host': self.getESHost(), 'port': self.getESPort()}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               buffer_size=500,
                               flush_frequency_in_sec=0.5,
                               es_index_name="pythontest")
        log = logging.getLogger("PythonTest")
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        for i in range(100):
            log.info("Logging line {0:d}".format(i), extra={'LineNum': i})
        handler.flush()
        self.assertEquals(0, len(handler._buffer))

if __name__ == '__main__':
    unittest.main()
