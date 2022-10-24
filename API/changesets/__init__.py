from enum import Enum
from geojson_pydantic.geometries import Polygon, MultiPolygon
from pydantic import validator
from typing import Union, Optional
from datetime import datetime, date
from typing import List
from .. import BaseModel


class FilterParams(BaseModel):
    geom: Optional[Union[Polygon, MultiPolygon]]
    hashtags: Optional[List[str]]
    from_timestamp: Optional[Union[datetime, date]]
    to_timestamp: Optional[Union[datetime, date]]
    project_ids: Optional[List[int]]

    @validator("to_timestamp", allow_reuse=True)
    def check_timestamp_diffs(cls, value, values, **kwargs):
        '''checks the timestamp difference '''

        from_timestamp = values.get("from_timestamp")
        timestamp_diff = value - from_timestamp
        if from_timestamp > value:
            raise ValueError(
                "Timestamp difference should be in order")
        return value
        """
         {
            "fromTimestamp":"2022-10-20T18:15:00.461",
            "toTimestamp":"2022-10-22T18:14:59.461",
            "hashtags":["missingmaps"]
        }
        """
    @validator("project_ids", allow_reuse=True)
    def check_other_fields(cls, value, values, **kwargs):
        '''checks existence of other fields '''

        from_timestamp = values.get("from_timestamp")
        to_timestamp = values.get("to_timestamp")
        hashtags = values.get("hashtags")
        geom = values.get("geom")
        if from_timestamp or to_timestamp or hashtags or geom:
            raise ValueError(
                "When projectid is supplied other fields are auto populated. Remove them")
        return value
        """
         {
            "fromTimestamp":"2022-10-20T18:15:00.461",
            "toTimestamp":"2022-10-22T18:14:59.461",
            "hashtags":["missingmaps"]
        }
        """