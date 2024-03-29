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

import json

from typing import List, Union, Optional
from pydantic import validator
from datetime import datetime, date, timedelta
from pydantic import BaseModel as PydanticModel

from pydantic import conlist
from geojson_pydantic import Feature, FeatureCollection, Point, Polygon
from enum import Enum
from area import area
import re

from ..config import config

MAX_POLYGON_AREA = 5000  # km^2

# this as argument in compile method
SPECIAL_CHARACTER = '[@!#$%^&*() <>?/\|}{~:,"]'  # noqa
ORGANIZATIONAL_FREQUENCY = {"w": 7, "m": 30, "q": 90, "y": 365}


def checkIfDuplicates(input_list):
    # converting all hashtags value to lowercase to check duplicates because MissingMaps and missingmaps both are treated same and considered as duplicate
    listOfElems = list(map(lambda x: x.lower(), input_list))
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True


def to_camel(string: str) -> str:
    split_string = string.split("_")

    return "".join(
        [split_string[0], *[w.capitalize() for w in split_string[1:]]])


class BaseModel(PydanticModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True


class MappedFeature(BaseModel):
    feature: str
    action: str
    count: int


class MapathonContributor(BaseModel):
    user_id: int
    username: str
    total_buildings: int
    editors: Optional[str]


class MappedFeatureWithUser(MappedFeature):
    username: str


class TimeSpentMapping(BaseModel):
    user_id: int
    time_spent_mapping: float


class TimeSpentValidating(BaseModel):
    user_id: int
    time_spent_validating: float


class MappedTaskStats(BaseModel):
    user_id: int
    tasks_mapped: int


class ValidatedTaskStats(BaseModel):
    user_id: int
    tasks_validated: int


class TMUserStats(BaseModel):
    tasks_mapped: List[MappedTaskStats]
    tasks_validated: List[ValidatedTaskStats]
    time_spent_mapping: List[TimeSpentMapping]
    time_spent_validating: List[TimeSpentValidating]


class MapathonSummary(BaseModel):
    total_contributors: int
    mapped_features: List[MappedFeature]


class MapathonDetail(BaseModel):
    mapped_features: List[MappedFeatureWithUser]
    contributors: List[MapathonContributor]
    tm_stats: List[TMUserStats]


class TimeStampParams(BaseModel):
    from_timestamp: Union[datetime, date]
    to_timestamp: Union[datetime, date]

    @validator("to_timestamp", allow_reuse=True)
    def check_timestamp_diffs(cls, value, values, **kwargs):
        '''checks the timestap difference '''

        from_timestamp = values.get("from_timestamp")

        # if from_timestamp > datetime.now() or value > datetime.now():
        #     raise ValueError(
        #         "Can not exceed current date and time")
        timestamp_diff = value - from_timestamp
        if from_timestamp > value:
            raise ValueError(
                "Timestamp difference should be in order")
        if timestamp_diff > timedelta(weeks=1):
            raise ValueError(
                "Timestamp difference must be lower than 1 week")

        return value


invalid_request_parameters = [" ", '"', '""', '" "']


class MapathonRequestParams(TimeStampParams):
    '''validation class for mapathon request parameter provided by user '''

    project_ids: List[int]
    hashtags: List[str]

    @validator("hashtags", allow_reuse=True)
    def check_hashtag_filter(cls, value, values, **kwargs):
        '''check the hashtag existence'''

        project_ids = values.get("project_ids")
        if len(project_ids) == 0 and len(value) == 0:
            raise ValueError(
                "Empty lists found for both hashtags and project_ids params")
        for v in value:
            if v == "":
                raise ValueError(
                    "Hashtag value contains unsupported character")
        if checkIfDuplicates(value) is True:
            raise ValueError("Hashtag Contains Duplicate entries")

        return value

class UsersListParams(BaseModel):
    user_names: List[str]
    from_timestamp: Union[datetime, date]
    to_timestamp: Union[datetime, date]

    @validator("user_names", allow_reuse=True)
    def validate_usernames(cls, value, **kwargs):
        '''check the length of usernames'''

        for name in value:
            osm_username_limit = 3
            if (len(name) < osm_username_limit):
                raise ValueError(
                    f"Usernames must have {osm_username_limit} characters or more.")
        return value


class DateStampParams(BaseModel):
    from_timestamp: Union[datetime, date]
    to_timestamp: Union[datetime, date]

    @validator("to_timestamp", allow_reuse=True)
    def check_timestamp_diffs(cls, value, values, **kwargs):
        '''checks the timestap difference '''

        from_timestamp = values.get("from_timestamp")
        timestamp_diff = value - from_timestamp

        # if from_timestamp > datetime.now() or value > datetime.now():
        #     raise ValueError(
        #         "Can not exceed current date and time")
        # Get the relativedelta between two dates
        if from_timestamp > value:
            raise ValueError(
                "Timestamp difference should be in order")
        if timestamp_diff > timedelta(days=31):
            raise ValueError(
                "Statistics is available for a maximum period of 1 month.")

        return value


class UserStatsParams(DateStampParams):
    user_id: int
    hashtags: List[str]
    project_ids: List[int] = []


class User(BaseModel):
    user_id: int
    user_name: str


class IssueType(Enum):
    BAD_GEOM = "badgeom"
    BAD_VALUE = "badvalue"
    INCOMPLETE = "incomplete"
    NO_TAGS = "notags"
    COMPLETE = "complete"
    ORPHAN = "orphan"
    OVERLAPPING = "overlaping"
    DUPLICATE = "duplicate"
    ALL = "all"  # if all is supplied rest of others will be ignored


class OutputType(Enum):
    CSV = "csv"
    GEOJSON = "geojson"


class DataQuality_TM_RequestParams(BaseModel):
    '''Request Parameteres validation for DataQuality Class Tasking Manager Project ID

    Parameters:
            “project_ids”:[int],
            “issue_type”: ["badgeom", "badvalue", "all"]

    Acceptance Criteria :
            project_ids: Required, Array can contain integer value only , Array can not be empty
            issue_type: Required, Only accepted value under supported issues ,Array can not be empty

    '''
    # using conlist of pydantic to refuse empty list
    project_ids: conlist(int, min_items=1)
    issue_types: List[IssueType]
    output_type: OutputType


class DataQuality_username_RequestParams(DateStampParams):
    '''Request Parameteres validation for DataQuality Class Username

    Parameters:
            osm_usernames:[str],
            “issue_type”: List[issuetypes]
            from_timestamp and to_timestamp
    '''
    # using conlist of pydantic to refuse empty list

    osm_usernames: conlist(str, min_items=1)
    issue_types: List[IssueType]
    hashtags: Optional[List[str]]
    output_type: OutputType

    @validator("hashtags", allow_reuse=True)
    def check_hashtag_string(cls, value, values, **kwargs):
        """Checks given hashtag string against special characters"""
        regex = re.compile(SPECIAL_CHARACTER)
        for v in value:
            v = v.strip()
            if len(v) < 2:
                raise ValueError(
                    "Hash tag value " + v + " is not allowed")

            if (regex.search(v) is not None):
                raise ValueError(
                    "Hash tag contains special character or space : " + v + " ,Which is not allowed")
        return value


class DataQualityProp(BaseModel):
    Osm_id: int
    Changeset_id: int
    Changeset_timestamp: Union[datetime, date]
    Issue_type: str


class DataQualityPointFeature(Feature):
    geometry: Point
    properties: DataQualityProp


class DataQualityPointCollection(FeatureCollection):
    """geojson pydantic models for data quality , Note : Not required if we will be using OUTPUT Class

    Args:
        FeatureCollection ([type]): [description]
    """
    features: List[DataQualityPointFeature]


class DataQualityHashtagParams(TimeStampParams):
    hashtags: Optional[List[str]]
    issue_type: List[IssueType]
    output_type: OutputType
    geometry: Optional[Polygon]

    @validator("geometry", always=True)
    def check_not_defined_fields(cls, value, values):
        """Checks given fields with geometry and hashtags"""
        hashtags = values.get("hashtags")

        if value is None and (hashtags is None or len(hashtags) == 0):
            raise ValueError("'geometry' and 'hashtags' fields not provided")

        if value is None:
            return

        area_m2 = area(json.loads(value.json()))
        area_km2 = area_m2 * 1E-6

        if area_km2 > MAX_POLYGON_AREA:
            raise ValueError("Polygon Area is higher than 5000 km^2")

        return value

class TrainingOrganisations(BaseModel):
    id: int
    name: str


class Trainings(BaseModel):
    tid: int
    name: str
    location: str = None
    organization: str = None
    eventtype: str = None
    topictype: str = None
    topics: str = None
    hours: int = None
    date: date


class EventType(Enum):
    VIRTUAL = "virtual"
    IN_PERSON = "inperson"


class TopicType(Enum):
    # JOSM = "josm"
    # ID_EDITOR = "ideditor"
    # VALIDATION = "validation"
    REMOTE = "remote"
    FIELD = "field"
    OTHER = "other"


class TrainingParams(BaseModel):
    """[Training Post API Parameter Validation Model]

    Args:
        BaseModel ([type]): [Pydantic Model]

    Raises:
        ValueError: [Timestamp difference should be in order]
        Unprocessable Entity: [If any skill type or event type is out of predefined Enum values]
    Returns:
        [value]: [Validated Parameters]
    """
    from_datestamp: Optional[date] = None
    to_datestamp: Optional[date] = None
    oid: Optional[int] = None
    topic_type: Optional[List[TopicType]] = None
    event_type: Optional[EventType] = None

    @validator("to_datestamp", allow_reuse=True)
    def check_timestamp_order(cls, value, values, **kwargs):
        '''checks the datestamps order '''
        from_datestamp = values.get("from_datestamp")
        if from_datestamp:
            if from_datestamp > value:
                raise ValueError(
                    "Timestamp should be in order")
        return value


class Frequency(Enum):
    WEEKLY = "w"
    MONTHLY = "m"
    QUARTERLY = "q"
    YEARLY = "y"


class OrganizationOutputtype(Enum):
    JSON = "json"
    CSV = "csv"


class OrganizationHashtagParams(BaseModel):
    hashtag: str
    frequency: Frequency
    output_type: OrganizationOutputtype
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @validator("hashtag", allow_reuse=True)
    def check_hashtag_string(cls, value, values, **kwargs):
        """Validates hashtags"""
        regex = re.compile(SPECIAL_CHARACTER)
        value = value.strip()
        if len(value) < 2:
            raise ValueError(
                "Hash tag value " + value + " is not allowed")

        if (regex.search(value) is not None):
            raise ValueError(
                "Hash tag contains special character or space : " + value + " ,Which is not allowed")
        return value

    @validator("end_date", allow_reuse=True)
    def check_date_difference(cls, value, values, **kwargs):
        """Validates date difference"""
        start_date = values.get("start_date")
        if start_date:
            frequency = values.get("frequency")
            difference = value - start_date
            if difference < timedelta(days=ORGANIZATIONAL_FREQUENCY[frequency]):
                raise ValueError(
                    f"""Minimum Date Difference is of {ORGANIZATIONAL_FREQUENCY[frequency]} days""")
        return value


class OrganizationHashtag(BaseModel):
    hashtag: str
    frequency: str
    start_date: date
    end_date: date
    total_new_buildings: int
    total_unique_contributors: int
    total_new_road_km: int
    total_new_amenities: int
    total_new_places: int


class TeamMemberFunction(Enum):
    """Describes the function a member can hold within a team"""

    MANAGER = 1
    MEMBER = 2

class HashtagParams(BaseModel):
    hashtags: Optional[List[str]]

    @validator("hashtags", allow_reuse=True)
    def check_hashtag_string(cls, value, values, **kwargs):
        """Validates hashtags"""
        regex = re.compile(SPECIAL_CHARACTER)
        for v in value:
            v = v.strip()
            if len(v) < 2:
                raise ValueError(
                    "Hash tag value " + v + " is not allowed")

            if (regex.search(v) is not None):
                raise ValueError(
                    "Hash tag contains special character or space : " + v + " ,Which is not allowed")
        return value

class SupportedFilters(Enum):
    TAGS = "tags"
    ATTRIBUTES = "attributes"

    @classmethod
    def has_value(cls, value):
        """Checks value"""
        return value in cls._value2member_map_


class SupportedGeometryFilters(Enum):
    POINT = 'point'
    LINE = 'line'
    POLYGON = 'polygon'
    ALLGEOM = 'all_geometry'

    @classmethod
    def has_value(cls, value):
        """Checks if the value is supported"""
        return value in cls._value2member_map_

class UserRole(Enum):
    ADMIN = 1
    STAFF = 2
    NONE = 3


class UserStatistics(BaseModel):
    added_buildings: int
    modified_buildings: int
    added_highway: int
    modified_highway: int
    added_highway_km: float
    modified_highway_km: float

class DataOutput(str, Enum):
    osm = "osm"
    mapathon_statistics = "mapathon_statistics"
    data_quality = "data_quality"
    user_statistics = "user_statistics"

class DataRecencyParams(BaseModel):
    data_output: DataOutput
