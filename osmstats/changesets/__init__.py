from enum import Enum
from geojson_pydantic.geometries import Polygon
from pydantic import ValidationError, validator
from pydantic.dataclasses import dataclass
from typing import Union, Optional, List
from datetime import datetime, date, timedelta

from .. import BaseModel


class InsightFeature(BaseModel):
    feature: str
    action: str
    count: int


class InsightReport(BaseModel):
    total_contributors: int
    mapped_features: List[InsightFeature]


class InsightsParams(BaseModel):
    project_ids: List[int]
    from_timestamp: Union[datetime, date]
    to_timestamp: Union[datetime, date]
    hashtags: List[str]

    @validator("to_timestamp")
    def check_timestamp_diffs(cls, value, values, **kwargs):
        from_timestamp = values.get("from_timestamp")
        timestamp_diff = value - from_timestamp
        if timestamp_diff > timedelta(hours=24):
            raise ValueError(
                "Timestamp difference must be lower than 24 hours"
            )

        return value

    @validator("hashtags")
    def check_hashtag_filter(cls, value, values, **kwargs):
        project_ids = values.get("project_ids")
        if len(project_ids) == 0 and len(value) == 0:
            raise ValueError(
                "Empty lists found for both hashtags and project_ids params"
            )

        return value


class PolygonFilter(Enum):
    iso3 = "iso3"
    geojson = "geojson"


class ChangesetResult(BaseModel):
    name: str
    total_changesets: int
    contributors: int
    added_highway: int
    modified_highway: int
    deleted_highway: int
    added_highway_km: float
    modified_highway_km: float
    deleted_highway_km: float


class FilterParams(BaseModel):
    type: PolygonFilter
    value: Union[str, Polygon]
    hashtag: Optional[str]
    start_datetime: Optional[Union[datetime, date]]
    end_datetime: Optional[Union[datetime, date]]

    @validator("type", "value")
    def matching_types(cls, v, values, **kwargs):
        type_val = values.get("type")
        if (
            "type" in values
            and values["type"].value == PolygonFilter.iso3.value
            and type(v) is not str
        ):
            raise ValueError("Value must be ISO3 code")

        if (
            "type" in values
            and values["type"].value == PolygonFilter.iso3.value
            and len(v) != 3
        ):
            raise ValueError("Invalid ISO3 code")

        if (
            "type" in values
            and values["type"].value == PolygonFilter.geojson.value
            and type(v) is not Polygon
        ):
            raise ValueError("Value must be geojson polygon")

        return v


"""
{
    "type": "geojson",
    "value": {
        "type": "Polygon",
        "coordinates": [
            [
                [-74.91995705, 10.91624758],
                [-74.75556731, 10.91624758],
                [-74.75556731, 11.10768916],
                [-74.91995705, 11.10768916],
                [-74.91995705, 10.91624758]
            ]
        ]
    }
}

"""
