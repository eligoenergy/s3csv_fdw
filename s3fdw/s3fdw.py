"""
An Amazon S3 Foreign Data Wrapper

"""
from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG

import boto3
import csv
from io import BytesIO, TextIOWrapper

# In at least some cases, bucket names are required to follow subdomain.domain
# format.
# Per https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
# Amazon recommends handling this by using custom TLS domain validation logic.
#
# Here we do so using a snippet posted by @ykhrustalev on
# https://github.com/boto/boto/issues/2836
import ssl

_old_match_hostname = ssl.match_hostname

def remove_dot(host):
    """
    >>> remove_dot('a.x.s3-eu-west-1.amazonaws.com')
    'ax.s3-eu-west-1.amazonaws.com'
    >>> remove_dot('a.s3-eu-west-1.amazonaws.com')
    'a.s3-eu-west-1.amazonaws.com'
    >>> remove_dot('s3-eu-west-1.amazonaws.com')
    's3-eu-west-1.amazonaws.com'
    >>> remove_dot('a.x.s3-eu-west-1.example.com')
    'a.x.s3-eu-west-1.example.com'
    """
    if not host.endswith('.amazonaws.com'):
        return host
    parts = host.split('.')
    h = ''.join(parts[:-3])
    if h:
        h += '.'
    return h + '.'.join(parts[-3:])


def _new_match_hostname(cert, hostname):
    return _old_match_hostname(cert, remove_dot(hostname))


ssl.match_hostname = _new_match_hostname

class S3Fdw(ForeignDataWrapper):
    """A foreign data wrapper for accessing csv files.

    Valid options:
        - aws_access_key : AWS access keys
        - aws_secret_key : AWS secret keys
        - hostname : accepted but ignored
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

        stream = BytesIO()
        s3.download_fileobj(self.bucket, self.filename, stream)
        stream.seek(0)

        reader = csv.reader(TextIOWrapper(stream, encoding='utf-8'), delimiter=self.delimiter, quotechar=self.quotechar)
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
                row=line[:len(self.columns)]
                nulled_row = [v if v else None for v in row]
                yield nulled_row
            count += 1

