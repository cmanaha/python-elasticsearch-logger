""" JSON serializer for Elasticsearch use
"""
from elasticsearch.serializer import JSONSerializer


class CMRESSerializer(JSONSerializer):
    """ JSON serializer inherited from the elastic search JSON serializer

    Allows to serialize logs for a elasticsearch use.
    Manage the record.exc_info containing an exception type.
    """
    def default(self, data):
        """ Default overrides the elasticsearch default method

        Allows to transform unknown types into strings

        :params data: The data to serialize before sending it to elastic search
        """
        try:
            return super(CMRESSerializer, self).default(data)
        except TypeError:
            return str(data)
