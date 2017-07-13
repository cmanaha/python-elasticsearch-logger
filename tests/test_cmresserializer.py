""" Test class for the serializers module
"""
import unittest
import logging
import datetime
import os
import sys
import decimal

sys.path.insert(0, os.path.abspath('.'))
from cmreslogging.serializers import CMRESSerializer


class CMRESSerializerTestCase(unittest.TestCase):
    """ CMRESSerializer test class
    """

    def setUp(self):
        """ Set up the test

        Set up the log and the formatter to get asctime and exc_text fields
        """
        self.log = logging.getLogger("MyTestCase")
        self.formatter = logging.Formatter('%(asctime)s')

    def tearDown(self):
        """ Delete the log and the formatter
        """
        del self.log
        del self.formatter

    def test_dumps_classic_log(self):
        """ Test the classic log serialization
        """
        serializer = CMRESSerializer()
        record = self.log.makeRecord(name=self.log.name,
                                     level=logging.INFO,
                                     fn=self.__class__.__name__,
                                     lno=58, msg="dump_classic_log",
                                     args=None, 
                                     exc_info=False,
                                     func=None,
                                     extra=None)
        self.formatter.format(record)
        for value in record.__dict__.values():
          try:
              serializer.dumps(value)
          except TypeError:
              self.fail("Serializer raised a TypeError exception")

    def test_dumps_exception_log(self):
        """ Test the exception log serialization with the exc_info field
        """
        serializer = CMRESSerializer()
        try:
            bad_idea = 1/0
        except ZeroDivisionError:
            record = self.log.makeRecord(name=self.log.name,
                                         level=logging.ERROR,
                                         fn=self.__class__.__name__,
                                         lno=58, msg="dump_exception_log",
                                         args=None, 
                                         exc_info=sys.exc_info(),
                                         func=None,
                                         extra=None)
        self.formatter.format(record)
        for value in record.__dict__.values():
            try:
                serializer.dumps(value)
            except TypeError:
                self.fail("Serializer raised a TypeError exception")

    def test_dumps_log_with_extras_and_args(self):
        """ Test the log serialization with arguments and extras complex parameters
        """
        serializer = CMRESSerializer()
        record = self.log.makeRecord(name=self.log.name,
                                     level=logging.ERROR,
                                     fn=self.__class__.__name__,
                                     lno=58, msg="dump_%s_log",
                                     args="args", 
                                     exc_info=False,
                                     func=None,
                                     extra={'complexvalue1': datetime.date.today(),
                                            'complexvalue2': decimal.Decimal('3.0')})
        self.formatter.format(record)
        for value in record.__dict__.values():
            try:
                serializer.dumps(value)
            except TypeError:
                self.fail("Serializer raised a TypeError exception")


if __name__ == '__main__':
  unittest.main()
