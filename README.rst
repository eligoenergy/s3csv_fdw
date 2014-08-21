============================================
S3 Csv Foreign Data Wrapper for Postgresql
============================================

This data wrapper allows to do 'select *' queries on CSV files stored
on S3 file system.  This is meant to replace s3_fdw that does is not
supported on PostgreSQL version 9.2+



Install multicorn
===========================================
First you need to activate multicorn extension in your pg database
::
    git clone git@github.com:eligoenergy/s3csv_fdw.git
    cd s3csv_fdw
    python setup.py install
Then in Postgres
::
    CREATE EXTENSION multicorn;



Create Foreign Data Wrapper
============================================

Just paste this code to create server
::
    CREATE SERVER multicorn_csv FOREIGN DATA WRAPPER multicorn
    options (
    	wrapper 's3csvfdw.s3csvfdw.S3CsvFdw'
    );
    


Create Foreign Table
============================================

You have to replace this example fileds from yours, fill in info ...

Example:
::
    CREATE FOREIGN TABLE test (
    	remote_filed1  character varying,
    	remote_field2  integer
    ) server multicorn_csv options(
    	bucket   'BUCKET',
    	filename 'FILENAME'
    );
    

Add user credentials
============================================

Store your aws credentials into a postgresql user mapping.

Example:
::
    CREATE USER MAPPING FOR my_pg_user SERVER multicorn_dynamo OPTIONS (aws_access_key_id  'XXXXXXXXXXXXXXX',aws_secret_access_key  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX');
    

Perform queries
============================================
You have a postgresql table now, for now, only read queries are working
::
    SELECT * from test;
    
Credits
=======

Christian Toivola (dev360) wrote the code and submited it as Multicorn
request here (https://github.com/Kozea/Multicorn/pull/49) .  I just
packeged it up.

