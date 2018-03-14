"""
An Amazon S3 Foreign Data Wrapper

"""
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG

import boto3
import csv
from cStringIO import StringIO

class S3Fdw(ForeignDataWrapper):
    """A foreign data wrapper for accessing csv files.

    Valid options:
        - aws_access_key : AWS access keys
        - aws_secret_key : AWS secret keys
        - bucket or bucketname : bucket in S3
        - filename : full path to the csv file, which must be readable
          with S3 credentials
        - delimiter : the delimiter used between fields.
          Default: ","
        - quotechar or quote : quote separator
        - skip_header or header: if integer, number of lines to skip, if true then 1, else 0
    """

    def __init__(self, fdw_options, fdw_columns):
        super(S3Fdw, self).__init__(fdw_options, fdw_columns)
        self.filename = fdw_options.get("filename")
        if self.filename is None:
            log_to_postgres("You must set filename", ERROR)


        self.bucket = fdw_options.get('bucket', 
                                      fdw_options.get('bucketname'))
        if self.bucket is None:
            log_to_postgres("You must set bucket", ERROR)

        self.aws_access_key = fdw_options['aws_access_key']
        self.aws_secret_key = fdw_options['aws_secret_key']

        self.delimiter = fdw_options.get("delimiter", ",")
        self.quotechar = fdw_options.get("quotechar", 
                                         fdw_options.get("quote", '"'))
        self.skip_header = int(fdw_options.get('skip_header') or 
                               1 if fdw_options.get('header') in ('T', 'TRUE', 't', 'true') else 0)
        self.columns = fdw_columns

    def execute(self, quals, columns):
        s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

        stream = StringIO()
        s3.download_fileobj(self.bucket, self.filename, stream)
        stream.seek(0)

        reader = csv.reader(stream, delimiter=self.delimiter, quotechar=self.quotechar)
        count = 0
        checked = False
        for line in reader:
            if count >= self.skip_header:
                if not checked:
                    # On first iteration, check if the lines are of the
                    # appropriate length
                    checked = True
                    if len(line) > len(self.columns):
                        log_to_postgres("There are more columns than "
                                        "defined in the table", WARNING)
                    if len(line) < len(self.columns):
                        log_to_postgres("There are less columns than "
                                        "defined in the table", WARNING)
                row = {}
                for i, (key, value)  in enumerate(self.columns.iteritems()):
                        column_name = key
                        if i > len(line) or line[i] == "":
                                row[column_name] = None
                        else:
                                row[column_name] = line[i]
                yield row
            count += 1

