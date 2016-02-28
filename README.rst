Python Elasticsearch Log handler
---------------------------------

This library provides an Elasticsearch logging appender compatible with the
pyton standard `logging<https://docs.python.org/2/library/logging.html>`_ library.

The code source is in github at `https://github.com/cmanaha/python-elasticsearch-logger<https://github.com/cmanaha/python-elasticsearch-logger>`_

Installation
------------

Install using pip 

::
    pip install CRMESHandler


Requirements
------------
This library requires the following dependencies
 - requests
 - requests-kerberos
 - elasticsearch
 - enum

Building the sources & Testing
------------------------------
To create the package follow the standard python setup.py to compile.

To test, just execute the python tests within the test folder



Setting up a log handler in your python program
-----------------------------------------------

Django integration
------------------

Why using an appender rather than logstash or beats
---------------------------------------------------

Contributing back
-----------------

