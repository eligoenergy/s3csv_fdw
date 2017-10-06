============================================
S3 CSV Foreign Data Wrapper for PostgreSQL
============================================
This data wrapper adds the ability to perform 'select *' queries on
CSV files stored on the Amazon S3 file system.  This is meant to
replace s3_fdw_ which is not supported on PostgreSQL version 9.2+.

.. _s3_fdw: https://github.com/umitanuki/s3_fdw


Install multicorn
===========================================
First you need to install it (last command might need a sudo).

.. code:: bash
    git clone git@github.com:eligoenergy/s3csv_fdw.git
    cd s3csv_fdw
    python setup.py install
Then activate multicorn extension in your pg database

.. code:: sql
    CREATE EXTENSION multicorn;


Create Foreign Data Wrapper
============================================
Just paste this code to create server

.. code:: sql
    CREATE SERVER multicorn_csv FOREIGN DATA WRAPPER multicorn
    options (
    	wrapper 's3csvfdw.s3csvfdw.S3CsvFdw'
    );


Create Foreign Table
============================================
Replace the example fields with your info...

Example:

.. code:: sql
    CREATE FOREIGN TABLE test (
    	remote_filed1  character varying,
    	remote_field2  integer
    ) server multicorn_csv options(
    	bucket   'BUCKET',
    	filename 'FILENAME'
    );


Add user credentials
============================================
Store your aws credentials into a PostgreSQL user mapping.

Example:

.. code:: sql
    CREATE USER MAPPING FOR my_pg_user SERVER multicorn_dynamo OPTIONS (aws_access_key_id  'XXXXXXXXXXXXXXX',aws_secret_access_key  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX');


Perform queries
============================================
You have a PostgreSQL table now, for now, only read queries are working.

.. code:: sql
    SELECT * from test;


Credits
============================================
Christian Toivola (dev360_) wrote the code and submitted it as Multicorn
request here (https://github.com/Kozea/Multicorn/pull/49).  I just
packaged it up.

.. _dev360: https://github.com/dev360
