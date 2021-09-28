from fastapi import Request, APIRouter, Depends, Header, HTTPException, status

import psycopg2

from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import Optional

from .. import config

from . import (
    MappedFeature,
    MapathonSummary,
    MapathonRequestParams
)

router = APIRouter(prefix="/mapathon")

@router.post("/summary", response_model=MapathonSummary)
def count_features(params: MapathonRequestParams):
    hstore_column = "tags"
    hashtag_project_ids = [f"%hotosm-project-{i}%" for i in params.project_ids]
    hashtag_filter_values = [
        *hashtag_project_ids,
        *[f"%{h}%" for h in params.hashtags],
    ]

    hstore_keys = ["hashtags", "comment"]
    timestamp_column = "created_at"

    db_params = dict(config.items("INSIGHTS_PG"))
    conn = psycopg2.connect(**db_params)

    cur = conn.cursor(cursor_factory=DictCursor)

    # Subquery to filter changesets matching hashtag and dates.
    hashtag_filter_query = "({hstore_column} -> %s) ~~ %s"
    hashtag_filter = [
        [
            cur.mogrify(hashtag_filter_query, (h, i)).decode()
            for h in hstore_keys
        ]
        for i in hashtag_filter_values
    ]

    # Flatten.
    hashtag_filter = [item for sublist in hashtag_filter for item in sublist]

    hashtag_filter = [
        sql.SQL(f).format(hstore_column=sql.Identifier(hstore_column))
        for f in hashtag_filter
    ]

    hashtag_filter = sql.SQL(" OR ").join(hashtag_filter).as_string(conn)

    timestamp_filter = sql.SQL("{timestamp_column} between %s AND %s").format(
        timestamp_column=sql.Identifier(timestamp_column)
    )
    timestamp_filter = cur.mogrify(
        timestamp_filter, (params.from_timestamp, params.to_timestamp)
    ).decode()

    changeset_query = f"SELECT id FROM osm_changeset WHERE {timestamp_filter} AND ({hashtag_filter})"

    # OSM element history query.
    osm_history_query = f"SELECT (each({hstore_column})).key AS feature, action, count(distinct id) AS count FROM osm_element_history where changeset in ({changeset_query}) group by feature, action ORDER BY count desc;"

    cur.execute(osm_history_query)
    result = cur.fetchall()

    mapped_features = [MappedFeature(**r) for r in result]

    # Get total contributors.
    cur.execute(
        f"SELECT COUNT(distinct user_id) as contributors_count from osm_changeset where {timestamp_filter} AND ({hashtag_filter})"
    )
    total_contributors = cur.fetchone().get("contributors_count")

    report = MapathonSummary(
        total_contributors=total_contributors, mapped_features=mapped_features
    )

    return report


