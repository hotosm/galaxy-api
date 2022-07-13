#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import logging

logging.getLogger("fiona").propagate = False  # disable fiona logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logging.getLogger('boto3').propagate = False

logger = logging.getLogger('galaxy')

CONFIG_FILE_PATH = "src/config.txt"

config = ConfigParser()
config.read(CONFIG_FILE_PATH)

AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY , BUCKET_NAME =None , None , None
#check either to use connection pooling or not 
if config.get('EXPORT_CONFIG', 'use_connection_pooling', fallback=None): 
    use_connection_pooling=True
else:
    use_connection_pooling=False

#check either to use s3 raw data exports file uploading or not 
if  config.get("EXPORT_UPLOAD", "FILE_UPLOAD_METHOD",fallback=None) == "s3":
    use_s3_to_upload=True
    try :
        AWS_ACCESS_KEY_ID=config.get("EXPORT_UPLOAD", "AWS_ACCESS_KEY_ID") 
        AWS_SECRET_ACCESS_KEY=config.get("EXPORT_UPLOAD", "AWS_SECRET_ACCESS_KEY")
    except :
        logging.DEBUG("No aws credentials supplied")
    BUCKET_NAME = config.get("EXPORT_UPLOAD", "BUCKET_NAME",fallback=None)
    if BUCKET_NAME is None : 
        BUCKET_NAME="exports-stage.hotosm.org" # default 
else:
    use_s3_to_upload=False

def get_db_connection_params(dbIdentifier: str) -> dict:
    """Return a python dict that can be passed to psycopg2 connections
    to authenticate to Postgres Databases

    Params: dbIdentifier: Section name of the INI config file containing
            database connection parameters

    Returns: connection_params (dict): PostgreSQL connection parameters
             corresponding to the configuration section.

    """

    ALLOWED_SECTION_NAMES = ('INSIGHTS', 'TM', 'UNDERPASS' , 'RAW_DATA')

    if dbIdentifier not in ALLOWED_SECTION_NAMES:
        print(f"Invalid dbIdentifier. Pick one of {ALLOWED_SECTION_NAMES}")
        return None
    try:
        connection_params = dict(config.items(dbIdentifier))
        return connection_params
    except Exception as ex :
        logging.error(f"""Can't find DB credentials on config :{dbIdentifier}""")
        return None