""" JSON serializer for Elasticsearch use
"""
from datetime import date, datetime
from decimal import Decimal

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
        if isinstance(data, (date, datetime)):
            return data.isoformat()
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return str(data)
