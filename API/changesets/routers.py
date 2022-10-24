import psycopg2

from psycopg2.extras import DictCursor
from fastapi import APIRouter
from fastapi_versioning import version
from .utils import geom_filter_subquery
from src.galaxy.config import get_db_connection_params
from src.galaxy.query_builder.builder import create_hashtagfilter_underpass, create_timestamp_filter_query
from . import  FilterParams
from io import StringIO
from csv import DictWriter
from fastapi.responses import StreamingResponse
from datetime import datetime
import json
router = APIRouter(prefix="/changesets")


@router.post("/")
@version(1)
def get_changesets(params: FilterParams):
    """Sample for getting changesets for a tasking manager projects :

    { "projectIds":[ 11372, 11373, 11374, 11375, 11376, 11377, 11378, 11379, 11380, 11381, 11382, 11383, 11384, 11385, 11386, 11387, 11388, 12020, 12022 ] }

    """
    underpass_db_params = get_db_connection_params("UNDERPASS")
    if params.project_ids :
        # if project id is supplied nothing is required from timestamp , to timestamp , hashtag are pre populated
        project_id_filters = []
        hashtag_ids=[]
        for i in params.project_ids:

            project_id_filters.append(f"""id={i}""")
            hashtag_ids.append(f"""hotosm-project-{i}""")

        project_id_filter_comb = " OR ".join(project_id_filters)
        tm_db_params = get_db_connection_params("TM")
        with psycopg2.connect(**tm_db_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query =f"""
                    select ST_AsGeoJSON(ST_Extent(p.geometry)), min(p.created), max(p.last_updated)
                    from projects p
                    where ({project_id_filter_comb})
                """
                cur.execute(query)
                tm_result = cur.fetchone()
        params.geom=json.loads(tm_result[0]) # gets bbox of task geometry
        params.from_timestamp=str(tm_result[1]) # gets min created timestamp of task
        params.to_timestamp=str(tm_result[2]) # gets max last updated timestamp of task
        params.hashtags=hashtag_ids # populate hashtags for projectid
    print(json.dumps(params.geom))
    print(params.from_timestamp)
    print(params.to_timestamp)
    hashtag_filter=create_hashtagfilter_underpass(params.hashtags,"hashtags")
    with psycopg2.connect(**underpass_db_params) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            timestamp_filter = create_timestamp_filter_query("created_at", params.from_timestamp, params.to_timestamp, cur)
            query =f"""
                SELECT
                    id
                from changesets c
                where
                    ({hashtag_filter}) and ({timestamp_filter})
            """
            if params.geom:
                 query+= f"""and ST_Intersects(ST_GEOMFROMGEOJSON('{json.dumps(params.geom)}') ,
                        c.bbox)"""
            cur.execute(query)
            result = cur.fetchall()

    stream = StringIO()

    if len(result) == 0:
        csv_stream= iter("")
    else:
        csv_keys = ["changeset_id","bbox","start_date","end_date"]

        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()
        writer.writerow({'bbox': json.dumps(params.geom),'start_date':params.from_timestamp,'end_date':params.to_timestamp})
        for item in result:
            row = {
                    'changeset_id': item[0]}

            writer.writerow(row)
        csv_stream= iter(stream.getvalue())
    response = StreamingResponse(csv_stream)
    exportname = f"Changesets_{datetime.now().isoformat()}"
    response.headers["Content-Disposition"] = f"attachment; filename={exportname}.csv"

    return response