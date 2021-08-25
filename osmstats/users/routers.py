import psycopg2

from fastapi import APIRouter
from psycopg2.extras import DictCursor
from typing import Optional

from .. import config
from osmstats.users import User, UsersResult

router = APIRouter(
    prefix="/users", 
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=UsersResult, response_model_exclude_unset=True)
def get_users(user_id: Optional[int] = None):
    db_params = dict(config.items("PG"))
    conn = psycopg2.connect(**db_params)

    cur = conn.cursor(cursor_factory=DictCursor)
    query = """
        with 
            t1 as (
                select 
                    cs.user_id,
                    coalesce(cs.added, hstore('none', '0')) AS added,
                    coalesce(cs.modified, hstore('none', '0')) AS modified,
                    coalesce(cs.deleted, hstore('none', '0')) AS deleted
                from changesets as cs
            ),
            t2 as (
                select
                    user_id, 
                    (each(added)).key as added_key,
                    (each(added)).value::numeric as added_value,
                    (each(modified)).key AS modified_key,
                    (each(modified)).value::numeric as modified_value,
                    (each(deleted)).key as deleted_key,
                    (each(deleted)).value::numeric as deleted_value
                from t1
            ),
            t3 as (
                select 
                    x.user_id, 
                    count(distinct(x.id)) as total_user_changesets
                from changesets as x, changesets as y
                where x.user_id = y.user_id
                group by x.user_id
            )
            select 
                t3.user_id,
                t3.total_user_changesets,
                coalesce(user_added_highway.added_total, 0) as added_highway,
                coalesce(user_modified_highway.modified_total, 0) as modified_highway,
                coalesce(user_deleted_highway.deleted_total, 0) as deleted_highway,
                coalesce(user_added_highway_km.added_total, 0) as added_highway_km,
                coalesce(user_modified_highway_km.modified_total, 0) as modified_highway_km,
                coalesce(user_deleted_highway_km.deleted_total, 0) as deleted_highway_km
            from t3
            left join (
                select 
                    user_id, 
                    added_key, 
                    sum(added_value) as added_total 
                from t2
                where added_key = 'highway'
                group by user_id, added_key
            )
            as user_added_highway
            on user_added_highway.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    modified_key, 
                    sum(modified_value) AS modified_total
                from t2
                where modified_key = 'highway'
                group by user_id, modified_key
            )
            as user_modified_highway
            on user_modified_highway.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    deleted_key, 
                    sum(deleted_value) AS deleted_total
                from t2
                where modified_key = 'highway'
                group by user_id, deleted_key
            )
            as user_deleted_highway
            on user_deleted_highway.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    added_key, 
                    sum(added_value) / 1000 AS added_total
                from t2
                where added_key = 'highway_km'
                group by user_id, added_key
            )
            as user_added_highway_km
            on user_added_highway_km.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    modified_key, 
                    sum(modified_value) / 1000 AS modified_total 
                from t2
                where modified_key = 'highway_km'
                group by user_id, modified_key
            )
            as user_modified_highway_km
            on user_modified_highway_km.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    deleted_key, 
                    sum(deleted_value) / 1000 AS deleted_total
                from t2
                where modified_key = 'highway_km'
                group by user_id, deleted_key
            )
            as user_deleted_highway_km
            on user_deleted_highway_km.user_id = t3.user_id
            
        """
    if user_id is not None:
        query = f"{query} where t3.user_id = {user_id}"

    cur.execute(query)
    result_dto = []
    result = cur.fetchall()

    for row in result:
        user_dto = User(**dict(row))
        result_dto.append(user_dto)

    return {"users": result_dto}

 
# subquery to extract changeset-keys/osm-tags
# t4 AS (
#             SELECT 
#                 DISTINCT((EACH(x.added)).key) AS "changeset_keys" 
#             FROM changesets x
#             UNION
#              SELECT 
#                 DISTINCT((EACH(y.modified)).key)
#             FROM changesets y
#             UNION
#              SELECT 
#                 DISTINCT((EACH(z.deleted)).key)
#             FROM changesets z
#             ;



