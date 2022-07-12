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

"""[Router Responsible for Raw data API ]
"""
import os
from uuid import uuid4
import json
from os.path import exists
from src.galaxy import config
from starlette.background import BackgroundTasks
import orjson
from http.client import REQUEST_ENTITY_TOO_LARGE
from fastapi import APIRouter, Depends, Request
from src.galaxy.query_builder.builder import remove_spaces
from src.galaxy.validation.models import RawDataHistoricalParams, RawDataCurrentParams,RawDataOutputType
from .auth import login_required
from src.galaxy.app import RawData,S3FileTransfer
from fastapi.responses import FileResponse, StreamingResponse
from datetime import datetime
import time
import zipfile
router = APIRouter(prefix="/raw-data")
from src.galaxy.config import logger as logging
import orjson
import os 
from starlette.background import BackgroundTasks
from .auth import login_required
from src.galaxy import config
from os.path import exists
import json
from uuid import uuid4
from .auth import login_required
import pathlib
import shutil
from src.galaxy.query_builder.builder import check_last_updated_rawdata
from src.galaxy.config import use_s3_to_upload
import requests
# @router.post("/historical-snapshot/")
# def get_historical_data(params:RawDataHistoricalParams):
#     start_time = time.time()
#     result= RawData(params).extract_historical_data()
#     return generate_rawdata_response(result,start_time)

@router.post("/current-snapshot/")
def get_current_data(params:RawDataCurrentParams,background_tasks: BackgroundTasks,request: Request):  
# def get_current_data(params:RawDataCurrentParams,background_tasks: BackgroundTasks, user_data=Depends(login_required)):
    start_time = time.time()
    logging.debug('Request Received from Raw Data API ')
    if params.output_type is None: # if no ouput type is supplied default is geojson output
        params.output_type=RawDataOutputType.GEOJSON.value

    # unique id for zip file and geojson for each export
    if params.file_name :
        formatted_file_name=remove_spaces(params.file_name) # need to format string from space to _ because it is filename , may be we need to filter special character as well later on
        # exportname = f"{formatted_file_name}_{datetime.now().isoformat()}_{str(uuid4())}"
        exportname = f"{formatted_file_name}_{str(uuid4())}_{params.output_type}" #disabled date for now

    else:
        # exportname = f"Raw_Export_{datetime.now().isoformat()}_{str(uuid4())}"
        exportname = f"Raw_Export_{str(uuid4())}_{params.output_type}"

    dump_temp_file, geom_area=RawData(params).extract_current_data(exportname)

    logging.debug('Zip Binding Started !')
    try:
        path = config.get("EXPORT_CONFIG", "path")
    except : 
        path = 'exports/' # first tries to import from config, if not defined creates exports in home directory 
    # saving file in temp directory instead of memory so that zipping file will not eat memory
    zip_temp_path = f"""{path}{exportname}.zip"""
    zf = zipfile.ZipFile(zip_temp_path, "w", zipfile.ZIP_DEFLATED)

    path=f"""{path}{exportname}/"""
    directory = pathlib.Path(path)
    for file_path in directory.iterdir():
        zf.write(file_path, arcname=file_path.name)

    # Compressing geojson file
    zf.writestr(f"""clipping_boundary.geojson""",
                orjson.dumps(dict(params.geometry)))

    zf.close()
    logging.debug('Zip Binding Done !')
    inside_file_size = 0
    for temp_file in dump_temp_file:
        # clearing tmp geojson file since it is already dumped to zip file we don't need it anymore
        if os.path.exists(temp_file):      
            inside_file_size += os.path.getsize(temp_file)
    
    #remove the file that are just binded to zip file , we no longer need to store it 
    background_tasks.add_task(remove_file, path)

    #check if download url will be generated from s3 or not from config
    if use_s3_to_upload :
        file_transfer_obj=S3FileTransfer()
        download_url=file_transfer_obj.upload(f"""exports/{exportname}.zip""",exportname)
        background_tasks.add_task(watch_s3_upload,download_url,zip_temp_path) # watches the status code of the link provided and deletes the file if it is 200
    else:
        try:
            client_host = config.get("EXPORT_CONFIG", "api_host")  # getting from config in case api and frontend is not hosted on same url
        except:
            client_host = f"""{request.url.scheme}://{request.client.host}"""  # getting client host
        
        try :
            client_port = config.get("EXPORT_CONFIG", "api_port")
        except:
            client_port = None
        if client_port :
            download_url = f"""{client_host}:{client_port}/exports/{exportname}.zip"""  # disconnected download portion from this endpoint because when there will be multiple hits at a same time we don't want function to get stuck waiting for user to download the file and deliver the response , we want to reduce waiting time and free function !
        else :
            download_url = f"""{client_host}/exports/{exportname}.zip"""  # disconnected download portion from this endpoint because when there will be multiple hits at a same time we don't want function to get stuck waiting for user to download the file and deliver the response , we want to reduce waiting time and free function !

    response_time = time.time() - start_time
    # getting file size of zip , units are in bytes converted to mb in response
    zip_file_size = os.path.getsize(zip_temp_path)
    response_time_str=""
    if int(response_time) < 60:
        response_time_str = f"""{int(response_time)} Seconds"""
    else:
        minute = int(response_time/60)
        if minute >= 60 :
            Hour = int(response_time/60)
            response_time_str= f"""{int(Hour)} Hour"""
            minute=minute-60*int(Hour)
        response_time_str += f"""{minute} Minute"""
    logging.debug("-------Raw : %s MB, %s :-: %s, %s Sqkm, format-%s-------" %
                  (round(inside_file_size/1000000), response_time_str,params.file_name,geom_area,params.output_type))
    return {"download_url": download_url, "file_name": exportname, "response_time": response_time_str, "query_area": f"""{geom_area} Sq Km """, "binded_file_size": f"""{round(inside_file_size/1000000)} MB""", "zip_file_size_bytes": {zip_file_size}}

@router.get("/status/")
def check_current_db_status():
    """Gives status about DB update, Substracts with current time and last db update time"""
    result = RawData().check_status()
    response = f"""{result} ago"""
    return {"last_updated": response}

def remove_file(path: str) -> None:
    """Used for removing temp file dir and its all content after zip file is delivered to user
    """
    try:
        shutil.rmtree(path)
    except OSError as e:
        logging.error("Error: %s - %s." % (e.filename, e.strerror))

def watch_s3_upload(url : str,path : str) -> None:
    """watches upload of s3 either it is completed or not and removes the temp file after completion

    Args:
        url (_type_): url generated by the script where data will be available
        path (_type_): path where temp file is located at 
    """
    start_time = time.time()
    remove_temp_file=True
    check_call=requests.get(url).status_code
    if check_call !=200 :
        while check_call !=200 :# check until status is not green
            check_call=requests.get(url).status_code
            if time.time() - start_time >300 :
                logging.error(f"""Upload time took more than 5 min , Killing watch : {path} , URL : {url}""")
                remove_temp_file=False # don't remove the file if upload fails
                break
            time.sleep(3) # check each 3 second
    #once it is verfied file is uploaded finally remove the file
    logging.debug(f"""File is uploaded at {url}""")
    if remove_temp_file :
        os.unlink(path)
        logging.debug(f"""File flushed out from {path}""")



