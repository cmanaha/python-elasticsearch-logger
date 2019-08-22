from elasticsearch import Elasticsearch, RequestsHttpConnection

MSG_KERBEROS = "Kerberos module not available. Please install \"requests-kerberos\""
MSG_AWS = "AWS4Auth not available. Please install \"requests-aws4auth\""
try:
    from requests_kerberos import HTTPKerberosAuth, DISABLED
    CMR_KERBEROS_SUPPORTED = True
except ImportError:
    CMR_KERBEROS_SUPPORTED = False

try:
    from requests_aws4auth import AWS4Auth
    AWS4AUTH_SUPPORTED = True
except ImportError:
    AWS4AUTH_SUPPORTED = False

NO_AUTH = 0
BASIC_AUTH = 1
KERBEROS_AUTH = 2
AWS_SIGNED_AUTH = 3


class ClientElasticSearch:

    def __init__(self, cmrs_handler):
        self._cmrs_handler = cmrs_handler

    @staticmethod
    def _validation_environment_error(value, msg_error):
        if not value:
            raise EnvironmentError(msg_error)


class ClientNotAuth(ClientElasticSearch):
    TYPE_CLIENT = NO_AUTH

    def __init__(self, cmrs_handler):
        ClientElasticSearch.__init__(self, cmrs_handler)

    def get(self):
        if self._cmrs_handler._client is None:
            self._cmrs_handler._client = Elasticsearch(hosts=self._cmrs_handler.hosts,
                                                       use_ssl=self._cmrs_handler.use_ssl,
                                                       verify_certs=self._cmrs_handler.verify_certs,
                                                       connection_class=RequestsHttpConnection,
                                                       serializer=self._cmrs_handler.serializer)

        return self._cmrs_handler._client


class ClientBasicAuth(ClientElasticSearch):
    TYPE_CLIENT = BASIC_AUTH

    def __init__(self, cmrs_handler):
        ClientElasticSearch.__init__(self, cmrs_handler)

    def get(self):

        if self._cmrs_handler._client is None:
            self._cmrs_handler._client = Elasticsearch(hosts=self._cmrs_handler.hosts,
                                                       http_auth=self._cmrs_handler.auth_details,
                                                       use_ssl=self._cmrs_handler.use_ssl,
                                                       verify_certs=self._cmrs_handler.verify_certs,
                                                       connection_class=RequestsHttpConnection,
                                                       serializer=self._cmrs_handler.serializer)

        return self._cmrs_handler._client


class ClientKerberos(ClientElasticSearch):
    TYPE_CLIENT = KERBEROS_AUTH

    def __init__(self, cmrs_handler):
        ClientElasticSearch.__init__(self, cmrs_handler)

    def get(self):
        self._validation_environment_error(CMR_KERBEROS_SUPPORTED, MSG_KERBEROS)

        # For kerberos we return a new client each time to make sure the tokens are up to date
        return Elasticsearch(hosts=self._cmrs_handler.hosts,
                             use_ssl=self._cmrs_handler.use_ssl,
                             verify_certs=self._cmrs_handler.verify_certs,
                             connection_class=RequestsHttpConnection,
                             http_auth=HTTPKerberosAuth(mutual_authentication=DISABLED),
                             serializer=self._cmrs_handler.serializer)


class ClientAmazon(ClientElasticSearch):
    TYPE_CLIENT = AWS_SIGNED_AUTH

    def __init__(self, cmrs_handler):
        ClientElasticSearch.__init__(self, cmrs_handler)

    def get(self):

        self._validation_environment_error(AWS4AUTH_SUPPORTED, MSG_AWS)
        if self._cmrs_handler._client is None:
            awsauth = AWS4Auth(self._cmrs_handler.aws_access_key,
                               self._cmrs_handler.aws_secret_key,
                               self._cmrs_handler.aws_region, 'es')
            self._cmrs_handler._client = Elasticsearch(
                hosts=self._cmrs_handler.hosts,
                http_auth=awsauth,
                use_ssl=self._cmrs_handler.use_ssl,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                serializer=self._cmrs_handler.serializer)

        return self._cmrs_handler._client


class FactoryClientES:

    CLIENTS = {NO_AUTH: ClientNotAuth,
               AWS_SIGNED_AUTH: ClientAmazon,
               BASIC_AUTH: ClientBasicAuth,
               KERBEROS_AUTH: ClientKerberos}

    @staticmethod
    def get_client(cmrs_handler):
        klass = FactoryClientES.CLIENTS.get(cmrs_handler.auth_type.value)
        if not klass:
            raise ValueError("Authentication method not supported")

        return klass(cmrs_handler)
