`Table of Contents`_

Python Elasticsearch Log handler
********************************

This library provides an Elasticsearch logging appender compatible with the
pyton standard `logging <https://docs.python.org/2/library/logging.html>`_ library.

The code source is in github at `https://github.com/cmanaha/python-elasticsearch-logger 
<https://github.com/cmanaha/python-elasticsearch-logger>`_


Installation
============

Install using pip::
    pip install CRMESHandler

Requirements
============
This library requires the following dependencies
 - requests
 - requests-kerberos
 - elasticsearch
 - enum

Setting up a log handler in your python program
-----------------------------------------------
To initialise and create the handler, just add the handler to your logger as follow::
    import CMRESHandler
    
    handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index")
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

You can add fields upon initialisation, providing more data of the execution context::
    import CMRESHandler
    
    handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=CMRESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index",
                               es_additional_fields={'App': 'MyAppName', 'Environment': 'Dev'})
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

This additional fields will be applied to all logging fields and recorded in elasticsearch

To log, use the regular commands from the logging library::
    log.info("This is an info statement that will be logged into elasticsearch")

Your code can also dump additional extra fields on a per log basis that can be used to instrument
operations. For example, when reading information from a database you could do something like::
    start_time = time.time()
    database_operation()
    db_delta = time.time() - start_time
    log.debug("Time it took to execute DB operation %.3f seconds" % db_delta, extra={'db_execution_time': db_delta})

The code above executes the DB operation, measures the time it took and logs an entry that contains
in the message the time the operation took as string and for convenience, it creates another field
called db_execution_time with a float that can be used to plot the time this operations are taking using
Kibana on top of elasticsearch


Django integration
------------------

Building the sources & Testing
------------------------------
To create the package follow the standard python setup.py to compile.
To test, just execute the python tests within the test folder

Why using an appender rather than logstash or beats
---------------------------------------------------

Contributing back
-----------------

