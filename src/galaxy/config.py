#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Humanitarian OpenStreetmap Team

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Humanitarian OpenStreetmap Team
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>

from configparser import ConfigParser
import logging

CONFIG_FILE_PATH = "src/config.txt"

config = ConfigParser()
config.read(CONFIG_FILE_PATH)

# get log level from config
log_level = config.get("API_CONFIG", "log_level", fallback=None)
use_s3_to_upload = False

if log_level is None or log_level.lower() == 'debug':  # default debug
    level = logging.DEBUG
elif log_level.lower() == 'info':
    level = logging.INFO
elif log_level.lower() == 'error':
    level = logging.ERROR
elif log_level.lower() == 'warning':
    level = logging.WARNING
else:
    logging.error(
        "logging config is not supported , Supported fields are : debug,error,warning,info , Logging to default :debug")
    level = logging.DEBUG

logging.getLogger("fiona").propagate = False  # disable fiona logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=level)
logging.getLogger('boto3').propagate = False  # disable boto3 logging

logger = logging.getLogger('galaxy')

export_path = config.get('API_CONFIG', 'export_path', fallback=None)
if export_path is None:
    export_path = "exports/"
if export_path.endswith("/") is False:
    export_path = f"""{export_path}/"""

shp_limit = int(config.get('API_CONFIG', 'shp_limit', fallback=4096))


AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME = None, None, None
# check either to use connection pooling or not
use_connection_pooling = config.getboolean(
    "API_CONFIG", "use_connection_pooling", fallback=False)

# check either to use s3 raw data exports file uploading or not
file_upload_method = config.get(
    "EXPORT_UPLOAD", "FILE_UPLOAD_METHOD", fallback='disk').lower()
if file_upload_method == "s3":
    use_s3_to_upload = True
    try:
        AWS_ACCESS_KEY_ID = config.get("EXPORT_UPLOAD", "AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = config.get(
            "EXPORT_UPLOAD", "AWS_SECRET_ACCESS_KEY")
    except Exception as ex:
        logging.debug(ex)
        logging.debug("No aws credentials supplied")
    BUCKET_NAME = config.get(
        "EXPORT_UPLOAD", "BUCKET_NAME", fallback="exports-stage.hotosm.org")
elif file_upload_method not in ["s3", "disk"]:
    logging.error(
        "value not supported for file_upload_method ,switching to default disk method")
    use_s3_to_upload = False

MAIN_API_URL = config.get("API_MONITORING", "MAIN_API_URL", fallback="http://127.0.0.1:8000/v1/")
ACCESS_TOKEN = config.get("API_MONITORING", "ACCESS_TOKEN", fallback=None)


def get_db_connection_params(dbIdentifier: str) -> dict:
    """Return a python dict that can be passed to psycopg2 connections
    to authenticate to Postgres Databases

    Params: dbIdentifier: Section name of the INI config file containing
            database connection parameters

    Returns: connection_params (dict): PostgreSQL connection parameters
             corresponding to the configuration section.

    """

    ALLOWED_SECTION_NAMES = ('INSIGHTS', 'TM', 'UNDERPASS', 'RAW_DATA')

    if dbIdentifier not in ALLOWED_SECTION_NAMES:
        logging.error(
            f"Invalid dbIdentifier. Pick one of {ALLOWED_SECTION_NAMES}")
        return None
    try:
        connection_params = dict(config.items(dbIdentifier))
        return connection_params
    except Exception as ex:
        logging.error(
            f"""Can't find DB credentials on config :{dbIdentifier}""")
        raise ex
