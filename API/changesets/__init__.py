from enum import Enum
from geojson_pydantic.geometries import Polygon, MultiPolygon
from pydantic import validator
from typing import Union, Optional
from datetime import datetime, date
from typing import List
from .. import BaseModel


class FilterParams(BaseModel):
    project_ids: Optional[List[int]]
    geom: Optional[Union[Polygon, MultiPolygon]]
    hashtags: List[str]
    from_timestamp: Union[datetime, date]
    to_timestamp: Union[datetime, date]

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