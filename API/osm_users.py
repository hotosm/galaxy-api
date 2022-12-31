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

from fastapi import APIRouter
from fastapi_versioning import version
from typing import List
from src.galaxy.validation.models import UsersListParams, User, UserStatsParams, UserStatistics
from src.galaxy.app import UserStats
router = APIRouter(prefix="/osm-users")


@router.post("/ids/", response_model=List[User])
@version(1)
def get_user_id(params: UsersListParams):
    """Provides OpenStreetMap user id of usernames, It is possible same username can be taken by different users at different times hence this endpoint takes from and to timestamps.

    Args:
        params (UsersListParams):

        {
        "userNames": [
            "string"
        ],
        "fromTimestamp": "string",
        "toTimestamp": "string"
        }

    Returns:
        json:

        {
            "userId": 0,
            "userName": "string"
        }

    Example Request :

        {
            "userNames":[
                "Kshitizraj Sharma"
            ],
            "fromTimestamp":"2022-04-26T00:00:00Z",
            "toTimestamp":"2022-04-27T00:00:00Z"
        }

    Example Response :

        [{"userId":123456,"userName":"Kshitizraj Sharma"}]
    """

    return UserStats().list_users(params)


@router.post("/statistics/", response_model=List[UserStatistics])
@version(1)
def get_user_statistics(params: UserStatsParams):
    """Returns Statistics for specified OpenStreetMap usernames over a period of time.

    Args:
        params (UserStatsParams):

        {
        "fromTimestamp": "string",
        "toTimestamp": "string",
        "userId": 0, # this will take only OpenStreetMap user id not user name; userId can be derived from /ids/ for one user at a time.
        "hashtags": [
            "string" # you can get user statistics for specific OpenStreetMap hashtag or
        ],
        "projectIds": []  # you can get user statistics for specific Tasking Manger Project IDs
        }

    Returns:

        {
            "addedBuildings": 0, #count
            "modifiedBuildings": 0, #count
            "addedHighway": 0, #count
            "modifiedHighway": 0, #count
            "addedHighwayKm": 0, #km
            "modifiedHighwayKm": 0 #km
        }

    Example Request :
    1. To get user stats within time period

        {
            "userId":7004124,
            "fromTimestamp":"2022-03-02T00:00:00Z",
            "toTimestamp":"2022-03-03T00:00:00Z",
            "projectIds":[],
            "hashtags":[]
        }

    2. To get stats contributed by user for particular OpenStreetMap hashtag :

        {
            "userId":7004124,
            "fromTimestamp":"2022-06-28T14:25:33.277Z",
            "toTimestamp":"2022-07-27T14:25:33.277Z",
            "projectIds":[],
            "hashtags":[
                "missingmaps"
            ]
        }

    3. To get stats contributed by user for specific Tasking Manager Project:

        {"userId":7004124,"fromTimestamp":"2022-06-28T14:25:33.277Z","toTimestamp":"2022-07-27T14:25:33.277Z","projectIds":[123],"hashtags":[]}
    """
    user_stats = UserStats()

    if len(params.hashtags) > 0:
        return user_stats.get_statistics_with_hashtags(params)

    return user_stats.get_statistics(params)
