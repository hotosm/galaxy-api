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

"""
  Router Responsible for Checking API Health 
"""

from fastapi import APIRouter
from fastapi_versioning import version
from src.galaxy.config import MAIN_API_URL
from src.galaxy.validation.models import SystemHealthOutput, SystemHealthType
from src.galaxy.app import SystemHealth
from .test_data import raw_data_testing_query, mapathon_testing_query

router = APIRouter(prefix="/health")

@router.get("/", response_model=SystemHealthOutput)
@version(1)
def check_system_health():
  """Simple health check for API accessibility"""

  authentication = SystemHealth().monitor_endpoint(endpoint=f'{MAIN_API_URL}/auth/login/', request_type='GET')
  mapathon_summary = SystemHealth().monitor_endpoint(endpoint=f'{MAIN_API_URL}/mapathon/summary/', request_type='POST', body=mapathon_testing_query)
  mapathon_detail = SystemHealth().monitor_endpoint(endpoint=f'{MAIN_API_URL}/mapathon/detail/', request_type='POST', body=mapathon_testing_query)
  raw_data = SystemHealth().monitor_endpoint(endpoint=f'{MAIN_API_URL}/raw-data/current-snapshot/', request_type='POST', body=raw_data_testing_query)

  return {
    "authentication" : SystemHealthType.HEALTHY.value if authentication == 200 else  SystemHealthType.UNHEALTHY.value,
    "mapathon_summary" : SystemHealthType.HEALTHY.value if mapathon_summary == 200 else  SystemHealthType.UNHEALTHY.value,
    "mapathon_detail" : SystemHealthType.HEALTHY.value if mapathon_detail == 200 else  SystemHealthType.UNHEALTHY.value,
    "raw_data" :  SystemHealthType.HEALTHY.value if raw_data == 200 else  SystemHealthType.UNHEALTHY.value
  }
   
    