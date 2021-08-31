import psycopg2
import datetime

from fastapi import APIRouter
from psycopg2.extras import DictCursor
from typing import Optional, List

from .. import config
from osmstats.users import User

router = APIRouter(
    prefix="/users", 
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[User], response_model_exclude_unset=True)
def get_users(user_id: Optional[int] = None, 
    tag: Optional[str] = None, 
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    ):
    db_params = dict(config.items("PG"))
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor(cursor_factory=DictCursor)

    t2 = f"""
            select
                user_id, 
                (each(added)).key as added_key,
                (each(added)).value::numeric as added_value,
                (each(modified)).key AS modified_key,
                (each(modified)).value::numeric as modified_value,
                (each(deleted)).key as deleted_key,
                (each(deleted)).value::numeric as deleted_value
            from t1
        """

    filters = []
    if start_date is not None:
        start_date_filter = f"created_at > '{start_date.isoformat()}'"
        filters.append(start_date_filter)
    if end_date is not None:
        end_date_filter = f"created_at < '{end_date.isoformat()}'"
        filters.append(end_date_filter)

    if len(filters) > 0:
        sq = " and ".join(filters)
        t2 = f"{t2} where {sq}"

    if tag is not None:
        osm_tag = tag
    else:
        osm_tag = 'highway'

    query = f"""
        with 
            t1 as (
                select 
                    cs.user_id,
                    cs.created_at,
                    coalesce(cs.added, hstore('none', '0')) AS added,
                    coalesce(cs.modified, hstore('none', '0')) AS modified,
                    coalesce(cs.deleted, hstore('none', '0')) AS deleted
                from changesets as cs
            ),
            t2 as ({t2}),
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
            coalesce(user_added_{osm_tag}.added_total, 0) as added_{osm_tag},
            coalesce(user_modified_{osm_tag}.modified_total, 0) as modified_{osm_tag},
            coalesce(user_deleted_{osm_tag}.deleted_total, 0) as deleted_{osm_tag}
        from t3
    """ 

    tag_query = f"""
        left join (
                select 
                    user_id, 
                    added_key, 
                    sum(added_value) as added_total 
                from t2
                where added_key = '{osm_tag}'
                group by user_id, added_key
            )
            as user_added_{osm_tag}
            on user_added_{osm_tag}.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    modified_key, 
                    sum(modified_value) AS modified_total
                from t2
                where modified_key = '{osm_tag}'
                group by user_id, modified_key
            )
            as user_modified_{osm_tag}
            on user_modified_{osm_tag}.user_id = t3.user_id
            left join (
                select 
                    user_id, 
                    deleted_key, 
                    sum(deleted_value) AS deleted_total
                from t2
                where modified_key = '{osm_tag}'
                group by user_id, deleted_key
            )
            as user_deleted_{osm_tag}
            on user_deleted_{osm_tag}.user_id = t3.user_id
        """

    query = f"{query} {tag_query}"

    if user_id is not None:
        query = f"{query} where t3.user_id = {user_id}"

    cur.execute(query)
    result_dto = []
    result = cur.fetchall()

    for row in result:  
        user_dto = User(
            **dict(row), 
            filtered_osm_tag=osm_tag, 
            added=float(row[f'added_{osm_tag}']), 
            modified=float(row[f'modified_{osm_tag}']), 
            deleted=float(row[f'deleted_{osm_tag}'])
        )
        result_dto.append(user_dto)

    return result_dto
