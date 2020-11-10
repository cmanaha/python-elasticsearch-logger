import os
import sys
import unittest
from enum import Enum

from cmreslogging.client_es import (ClientAmazon, ClientBasicAuth,
                                    ClientKerberos, ClientNotAuth,
                                    FactoryClientES)
from cmreslogging.handlers import CMRESHandler

sys.path.insert(0, os.path.abspath('.'))


class AuthTypeFake(Enum):
    NO_AUTH = 10


class ClientESTestCase(unittest.TestCase):

    def crms_handler(self, type_client_es):
        return CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                            auth_type=type_client_es,
                            es_index_name="my_python_index",
                            es_additional_fields={'App': 'MyAppName', 'Environment': 'Dev'})

    def test_get_client_no_auth(self):
        cmr_handler = self.crms_handler(CMRESHandler.AuthType.NO_AUTH)
        client = FactoryClientES.get_client(cmr_handler)
        self.assertIsInstance(client, ClientNotAuth)

    def test_get_client_auth_basic(self):
        cmr_handler = self.crms_handler(CMRESHandler.AuthType.BASIC_AUTH)
        client = FactoryClientES.get_client(cmr_handler)
        self.assertIsInstance(client, ClientBasicAuth)

    def test_get_client_amazon(self):
        cmr_handler = self.crms_handler(CMRESHandler.AuthType.AWS_SIGNED_AUTH)
        client = FactoryClientES.get_client(cmr_handler)
        self.assertIsInstance(client, ClientAmazon)

    def test_get_client_kerberos(self):
        cmr_handler = self.crms_handler(CMRESHandler.AuthType.KERBEROS_AUTH)
        client = FactoryClientES.get_client(cmr_handler)
        self.assertIsInstance(client, ClientKerberos)

    def test_execption_value_error(self):
        cmr_handler = self.crms_handler(AuthTypeFake.NO_AUTH)
        with self.assertRaises(ValueError):
            FactoryClientES.get_client(cmr_handler)


if __name__ == '__main__':
    unittest.main()
