
===============
CMRESHandler.py
===============

|  |license| |versions| |status| |downloads|
|  |ci_status| |codecov| |gitter|


Python Elasticsearch Log handler
********************************

This library provides an Elasticsearch logging appender compatible with the
python standard `logging <https://docs.python.org/2/library/logging.html>`_ library.

The code source is in github at `https://github.com/cmanaha/python-elasticsearch-logger
<https://github.com/cmanaha/python-elasticsearch-logger>`_


Installation
============
Install using pip::

    pip install CMRESHandler

Requirements
============
This library requires the following dependencies
 - requests
 - requests-kerberos
 - elasticsearch
 - enum

Using the handler in  your program
==================================
To initialise and create the handler, just add the handler to your logger as follow ::

    import CMRESHandler
    handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index")
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

You can add fields upon initialisation, providing more data of the execution context ::

    import CMRESHandler
    handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index",
                               es_additional_fields={'App': 'MyAppName', 'Environment': 'Dev'})
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

This additional fields will be applied to all logging fields and recorded in elasticsearch

To log, use the regular commands from the logging library ::

    log.info("This is an info statement that will be logged into elasticsearch")

Your code can also dump additional extra fields on a per log basis that can be used to instrument
operations. For example, when reading information from a database you could do something like::

    start_time = time.time()
    database_operation()
    db_delta = time.time() - start_time
    log.debug("DB operation took %.3f seconds" % db_delta, extra={'db_execution_time': db_delta})

The code above executes the DB operation, measures the time it took and logs an entry that contains
in the message the time the operation took as string and for convenience, it creates another field
called db_execution_time with a float that can be used to plot the time this operations are taking using
Kibana on top of elasticsearch

Initialisation parameters
=========================
The constructors takes the following parameters:
 - hosts:  The list of hosts that elasticsearch clients will connect, multiple hosts are allowed, for example ::

    [{'host':'host1','port':9200}, {'host':'host2','port':9200}]


 - auth_type: The authentication currently support CMRESHandler.AuthType = NO_AUTH, BASIC_AUTH, KERBEROS_AUTH
 - auth_details: When CMRESHandler.AuthType.BASIC_AUTH is used this argument must contain a tuple of string with the user and password that will be used to authenticate against the Elasticsearch servers, for example ('User','Password')
 - use_ssl: A boolean that defines if the communications should use SSL encrypted communication
 - verify_ssl: A boolean that defines if the SSL certificates are validated or not
 - buffer_size: An int, Once this size is reached on the internal buffer results are flushed into ES
 - flush_frequency_in_sec: A float representing how often and when the buffer will be flushed
 - es_index_name: A string with the prefix of the elasticsearch index that will be created. Note a date with
   YYYY.MM.dd, ``python_logger`` used by default
 - es_doc_type: A string with the name of the document type that will be used ``python_log`` used by default
 - es_additional_fields: A dictionary with all the additional fields that you would like to add to the logs

Django Integration
==================
It is also very easy to integrate the handler to `Django <https://www.djangoproject.com/>`_ And what is even
better, at DEBUG level django logs information such as how long it takes for DB connections to return so
they can be plotted on Kibana, or the SQL statements that Django executed. ::

    from cmreshandler.cmreshandler import CMRESHandler
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': './debug.log',
                'maxBytes': 102400,
                'backupCount': 5,
            },
            'elasticsearch': {
                'level': 'DEBUG',
                'class': 'cmreshandler.cmreshandler.CMRESHandler',
                'hosts': [{'host': 'localhost', 'port': 9200}],
                'es_index_name': 'my_python_app',
                'es_additional_fields': {'App': 'Test', 'Environment': 'Dev'},
                'auth_type': CMRESHandler.AuthType.NO_AUTH,
                'use_ssl': False,
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file','elasticsearch'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

There is more information about how Django logging works in the
`Django documentation <https://docs.djangoproject.com/en/1.9/topics/logging//>`_


Building the sources & Testing
------------------------------
To create the package follow the standard python setup.py to compile.
To test, just execute the python tests within the test folder

Why using an appender rather than logstash or beats
---------------------------------------------------
In some cases is quite useful to provide all the information available within the LogRecords as it contains
things such as exception information, the method, file, log line where the log was generated. All this can be
also done from logstash configuration, but it still requires to provide quite a lot of context to

Contributing back
-----------------
Feel free to use this as is or even better, feel free to fork and send your pull requests over.


.. |downloads| image:: https://img.shields.io/pypi/dd/CMRESHandler.svg
    :target: https://pypi.python.org/pypi/CMRESHandler
    :alt: Daily PyPI downloads
.. |versions| image:: https://img.shields.io/pypi/pyversions/CMRESHandler.svg
    :target: https://pypi.python.org/pypi/CMRESHandler
    :alt: Python versions supported
.. |status| image:: https://img.shields.io/pypi/status/CMRESHandler.svg
    :target: https://pypi.python.org/pypi/CMRESHandler
    :alt: Package stability
.. |license| image:: https://img.shields.io/pypi/l/CMRESHandler.svg
    :target: https://pypi.python.org/pypi/CMRESHandler
    :alt: License
.. |ci_status| image:: https://travis-ci.org/cmanaha/python-elasticsearch-logger.svg?branch=master
    :target: https://travis-ci.org/cmanaha/python-elasticsearch-logger
    :alt: Continuous Integration Status
.. |codecov| image:: https://codecov.io/github/cmanaha/python-elasticsearch-logger/coverage.svg?branch=master
    :target: http://codecov.io/github/cmanaha/python-elasticsearch-logger?branch=master
    :alt: Coverage!
.. |gitter| image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/cmanaha/python-elasticsearch-logger?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
    :alt: gitter
