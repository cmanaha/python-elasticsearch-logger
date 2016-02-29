import unittest
import logging
import time
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from cmreshandler.cmreshandler import CMRESHandler


class CMRESHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("MyTestCase")
        test_handler = logging.StreamHandler(stream=sys.stderr)
        self.log.addHandler(test_handler)

    def tearDown(self):
        del self.log

    def test_ping(self):
        handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="pythontest",
                               use_ssl=False)
        es_test_server_is_up = handler.test_es_source()
        self.assertEquals(True, es_test_server_is_up)

    def test_es_log_extra_argument_insertion(self):
        self.log.info("About to test elasticsearch insertion")
        handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  %s" % es_test_server_is_up)
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
        handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               flush_frequency_in_sec=0.1,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  %s" % es_test_server_is_up)
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

    def test_buffered_log_insertion_flushed_when_buffer_full(self):
        handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               buffer_size=2,
                               flush_frequency_in_sec=1000,
                               es_index_name="pythontest",
                               es_additional_fields={'App': 'Test', 'Environment': 'Dev'})

        es_test_server_is_up = handler.test_es_source()
        self.log.info("ES services status is:  %s" % es_test_server_is_up)
        self.assertEquals(True, es_test_server_is_up)

        log = logging.getLogger("PythonTest")
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        log.warning("First Message")
        log.info("Seccond Message")
        self.assertEquals(0, len(handler._buffer))
        handler.close()

    def test_fast_insertion_of_thousands_logs(self):
        handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               use_ssl=False,
                               buffer_size=200,
                               flush_frequency_in_sec=0.1,
                               es_index_name="pythontest")
        log = logging.getLogger("PythonTest")
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        for i in xrange(1000):
            log.info("Logging line %d" % i, extra={'LineNum': i})
        time.sleep(0.5)
        self.assertEquals(0, len(handler._buffer))


if __name__ == '__main__':
    unittest.main()
