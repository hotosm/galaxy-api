from fastapi import APIRouter
from src.galaxy.app import Database
from src.galaxy.config import get_db_connection_params
router = APIRouter()

@router.get("/test_changeset/{start_date}/{end_date}/{hashtag}")
def test_changeset_difference(start_date,end_date,hashtag):
    """
    sample request : 
    start_date : 2018-08-09
    end_date : 2018-08-10
    hashtag : missingmaps
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
    insight_query_changeset_id_list=f"""with t1 as (
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
                        distinct id
                    from
                        t1 ,
                        geoboundaries as g
                    where
                        ST_Intersects(t1.geom ,
                        ST_SetSRID(g.boundary,
                        4326));"""                 
                        
    underpass_query=f"""select
                            COUNT(distinct id) as total_changeset_found_with_hashtag
                        from
                            changesets
                        where
                            ("created_at" between '{start_date}T00:00:00'::timestamp and '{end_date}T00:00:00'::timestamp)
                            and ('{hashtag}' ~~* any(hashtags))"""
    insight=Database(get_db_connection_params("INSIGHTS"))
    insight.connect()
    # print(insight_query)
    
    insight_result=insight.executequery(insight_query)
    # print(insight_query_changeset_id_list)
    insight_changeset_list=insight.executequery(insight_query_changeset_id_list)

    insight.close_conn()
    
    changeset_list_within_proiority_insight=[]
    for r in insight_changeset_list:
        changeset_list_within_proiority_insight.append(f"""id={r[0]}""")
    filter_changeset_list = " or ".join(changeset_list_within_proiority_insight)
    underpass_changeset_check_query=f"""select
                            COUNT(distinct id) as total_changeset_found_with_id
                        from
                            changesets
                        where
                            {filter_changeset_list}"""
    # print(underpass_changeset_check_query)
    underpass = Database(get_db_connection_params("UNDERPASS"))
    underpass.connect()
    # print(underpass_query)
    
    underpass_result=underpass.executequery(underpass_query)
    underpass_result_for_id=underpass.executequery(underpass_changeset_check_query)
    
    underpass.close_conn()
    

    

    return {
        "insight_changeset_intersected_priority_count" : insight_result[0][0],
        "underpass_changeset_count_#" : underpass_result[0][0],
        "underpass_changeset_count_id" : underpass_result_for_id[0][0],
        "changeset_with_metadata_missing" :insight_result[0][0]-underpass_result[0][0],
        "whole_changeset_row_missing" :insight_result[0][0]- underpass_result_for_id[0][0],
        
        
    }