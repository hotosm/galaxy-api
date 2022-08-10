from fastapi import APIRouter
from src.galaxy.app import Database
from src.galaxy.config import get_db_connection_params
router = APIRouter()

@router.get("/test_changeset/{start_date}/{end_date}/{hashtag}")
def root(start_date,end_date,hashtag):
    """
    date format : 2018-08-10
    """
    insight_query=f"""with t1 as (
                    select
                        geom ,
                        id
                    from
                        osm_changeset
                    where
                        "created_at" between '{start_date}T00:00:00'::timestamp and '{end_date}T00:00:00'::timestamp
                        and (("tags" -> 'hashtags') ~~* '%{hashtag};%'
                            or ("tags" -> 'comment') ~~* '%{hashtag} %'
                                or ("tags" -> 'hashtags') ~~* '%{hashtag}'
                                    or ("tags" -> 'comment') ~~* '%{hashtag}'))
                    select
                        count(distinct id) as intersected_changeset_count
                    from
                        t1 ,
                        geoboundaries as g
                    where
                        ST_Intersects(t1.geom ,
                        ST_SetSRID(g.boundary,
                        4326));"""
    underpass_query=f"""select
                            COUNT(distinct id) as total_changeset_count
                        from
                            changesets
                        where
                            ("created_at" between '{start_date}T00:00:00'::timestamp and '{end_date}T00:00:00'::timestamp)
                            and ('{hashtag}' ~~* any(hashtags))"""
    underpass = Database(get_db_connection_params("UNDERPASS"))
    underpass.connect()
    print(underpass_query)
    
    underpass_result=underpass.executequery(underpass_query)
    
    insight=Database(get_db_connection_params("INSIGHTS"))
    insight.connect()
    print(insight_query)
    
    insight_result=insight.executequery(insight_query)

    return {
        "insight" : insight_result[0][0],
        "underpass" : underpass_result[0][0],
        "difference" :insight_result[0][0]-underpass_result[0][0]
    }