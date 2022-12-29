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

from psycopg2 import sql
from json import dumps
from ..validation.models import Frequency
HSTORE_COLUMN = "tags"


def create_hashtag_filter_query(project_ids, hashtags, cur, conn, prefix=False):
    '''returns hashtag filter query '''

    # merged_items = [*project_ids , *hashtags]
    if prefix:  # default prefix is c
        filter_query = "(c.{hstore_column} -> %s) ~~* %s"
    else:
        filter_query = "({hstore_column} -> %s) ~~* %s"

    hashtag_filter_values = [
        *[f"%hotosm-project-{i};%" if project_ids is not None else '' for i in project_ids],
        *[f"%{i};%" for i in hashtags],
    ]
    hashtag_tags_filters = [
        cur.mogrify(filter_query, ("hashtags", i)).decode()
        for i in hashtag_filter_values
    ]

    comment_filter_values = [
        *[f"%hotosm-project-{i} %" if project_ids is not None else '' for i in project_ids],
        *[f"%{i} %" for i in hashtags],
    ]
    comment_tags_filters = [
        cur.mogrify(filter_query, ("comment", i)).decode()
        for i in comment_filter_values
    ]

    # Include cases for hasthags and comments found at the end of the string.
    no_char_filter_values = [
        *[f"%hotosm-project-{i}" if project_ids is not None else '' for i in project_ids],
        *[f"%{i}" for i in hashtags],
    ]
    no_char_filter_values = [
        [cur.mogrify(filter_query, (k, i)).decode()
         for k in ("hashtags", "comment")]
        for i in no_char_filter_values
    ]

    no_char_filter_values = [
        item for sublist in no_char_filter_values for item in sublist]

    hashtag_filter = [*hashtag_tags_filters,
                      *comment_tags_filters, *no_char_filter_values]

    hashtag_filter = [
        sql.SQL(f).format(hstore_column=sql.Identifier(HSTORE_COLUMN))
        for f in hashtag_filter
    ]

    hashtag_filter = sql.SQL(" OR ").join(hashtag_filter).as_string(conn)

    return hashtag_filter


def create_timestamp_filter_query(column_name, from_timestamp, to_timestamp, cur, prefix=False):
    '''returns timestamp filter query '''

    timestamp_column = column_name
    # Subquery to filter changesets matching hashtag and dates.
    if prefix:
        timestamp_filter = sql.SQL("c.{timestamp_column} between %s AND %s").format(
            timestamp_column=sql.Identifier(timestamp_column))
    else:
        timestamp_filter = sql.SQL("{timestamp_column} between %s AND %s").format(
            timestamp_column=sql.Identifier(timestamp_column))
    timestamp_filter = cur.mogrify(timestamp_filter,
                                   (from_timestamp, to_timestamp)).decode()

    return timestamp_filter


def create_changeset_query(params, conn, cur):
    '''returns the changeset query'''

    hashtag_filter = create_hashtag_filter_query(params.project_ids,
                                                 params.hashtags, cur, conn)
    timestamp_filter = create_timestamp_filter_query("created_at", params.from_timestamp,
                                                     params.to_timestamp, cur)

    changeset_query = f"""
    SELECT user_id, id as changeset_id, user_name as username
    FROM osm_changeset
    WHERE {timestamp_filter} AND ({hashtag_filter})
    """

    return changeset_query, hashtag_filter, timestamp_filter

def create_userstats_get_statistics_with_hashtags_query(params, con, cur):

    filter_hashtags = create_hashtagfilter_underpass(params.hashtags, "hashtags")
    timestamp_filter = create_timestamp_filter_query(
        "created_at", params.from_timestamp, params.to_timestamp, cur, prefix=True)
    query = f"""
    SELECT
    sum((added->'building')::numeric) AS added_buildings,
    sum((modified->'building')::numeric) AS modified_buildings,
    sum((added->'highway')::numeric) AS added_highway,
    sum((modified->'highway')::numeric) AS modified_highway,
    sum((added->'highway_km')::numeric) AS added_highway_meters,
    sum((modified->'highway_km')::numeric) AS modified_highway_meters
    FROM changesets c
    WHERE {timestamp_filter}
    AND user_id = {params.user_id}
    AND {filter_hashtags};
    """
    return query

def create_UserStats_get_statistics_query(params, con, cur):
    query = """
    SELECT
    sum((added->'building')::numeric) AS added_buildings,
    sum((modified->'building')::numeric) AS modified_buildings,
    sum((added->'highway')::numeric) AS added_highway,
    sum((modified->'highway')::numeric) AS modified_highway,
    sum((added->'highway_km')::numeric) AS added_highway_meters,
    sum((modified->'highway_km')::numeric) AS modified_highway_meters
    FROM changesets
    WHERE created_at BETWEEN %s AND %s
    AND user_id = %s;
    """
    items = (params.from_timestamp, params.to_timestamp, params.user_id)
    query = cur.mogrify(query, items)
    return query

def create_users_contributions_query(params, changeset_query):
    '''returns user contribution query'''

    from_timestamp = params.from_timestamp.isoformat()
    to_timestamp = params.to_timestamp.isoformat()

    query = f"""
        with t0 as (
        SELECT user_id, array_agg(distinct (editor)) as editor
            FROM changesets c
            WHERE added->'building' is not null
            and created_at BETWEEN '{from_timestamp}' AND '{to_timestamp}'
            group by user_id
        ),
        t1 as (
            SELECT added->'building' as added_buildings, user_id, username
            FROM changesets c
            INNER JOIN users u ON u.id = c.user_id
            WHERE added->'building' is not null
            and created_at BETWEEN {from_timestamp}' AND '{to_timestamp}'
            group by user_id, username, added_buildings
        )
        select t1.user_id, username, sum(added_buildings::numeric) as total_buildings, editor from t1
        inner join t0 on t0.user_id = t1.user_id
        group by t1.user_id, username, editor;
    """
    return query


def create_user_tasks_mapped_and_validated_query(project_ids, from_timestamp, to_timestamp):
    tm_project_ids = ",".join([str(p) for p in project_ids])

    mapped_query = f"""
        SELECT th.user_id, COUNT(th.task_id) as tasks_mapped
            FROM PUBLIC.task_history th
            WHERE th.action_text = 'MAPPED'
            AND th.action_date BETWEEN '{from_timestamp}' AND '{to_timestamp}'
            AND th.project_id IN ({tm_project_ids})
            GROUP BY th.user_id;
    """
    validated_query = f"""
        SELECT th.user_id, COUNT(th.task_id) as tasks_validated
            FROM PUBLIC.task_history th
            WHERE th.action_text = 'VALIDATED'
            AND th.action_date BETWEEN '{from_timestamp}' AND '{to_timestamp}'
            AND th.project_id IN ({tm_project_ids})
            GROUP BY th.user_id;
    """
    return mapped_query, validated_query


def create_user_time_spent_mapping_and_validating_query(project_ids, from_timestamp, to_timestamp):
    tm_project_ids = ",".join([str(p) for p in project_ids])

    time_spent_mapping_query = f"""
        SELECT user_id, SUM(CAST(TO_TIMESTAMP(action_text, 'HH24:MI:SS') AS TIME)) AS time_spent_mapping
        FROM public.task_history
        WHERE
            (action = 'LOCKED_FOR_MAPPING'
            OR action = 'AUTO_UNLOCKED_FOR_MAPPING')
            AND action_date BETWEEN '{from_timestamp}' AND '{to_timestamp}'
            AND project_id IN ({tm_project_ids})
        GROUP BY user_id;
    """

    time_spent_validating_query = f"""
        SELECT user_id, SUM(CAST(TO_TIMESTAMP(action_text, 'HH24:MI:SS') AS TIME)) AS time_spent_validating
        FROM public.task_history
        WHERE action = 'LOCKED_FOR_VALIDATION'
            AND action_date BETWEEN '{from_timestamp}' AND '{to_timestamp}'
            AND project_id IN ({tm_project_ids})
        GROUP BY user_id;
    """
    return time_spent_mapping_query, time_spent_validating_query


def generate_data_quality_hashtag_reports(cur, params):
    if params.hashtags is not None and len(params.hashtags) > 0:
        filter_hashtags = ", ".join(["%s"] * len(params.hashtags))
        filter_hashtags = cur.mogrify(
            sql.SQL(filter_hashtags), params.hashtags).decode()
        filter_hashtags = f"AND unnest_hashtags in ({filter_hashtags})"
    else:
        filter_hashtags = ""

    if params.geometry is not None:
        geometry_dump = dumps(dict(params.geometry))
        geom_filter = f"WHERE ST_CONTAINS(ST_GEOMFROMGEOJSON('{geometry_dump}'), location)"
    else:
        geom_filter = ""

    issue_types = ", ".join(["%s"] * len(params.issue_type))
    issue_types_str = [i for i in params.issue_type]
    issue_types = cur.mogrify(sql.SQL(issue_types), issue_types_str).decode()

    timestamp_filter = cur.mogrify(sql.SQL(
        "created_at BETWEEN %s AND %s"), (params.from_timestamp, params.to_timestamp)).decode()

    query = f"""
        WITH t1 AS (SELECT osm_id, change_id, values, st_x(location) AS lat, st_y(location) AS lon, unnest(status) AS unnest_status from validation {geom_filter}),
        t2 AS (SELECT id, created_at, unnest(hashtags) AS unnest_hashtags from changesets WHERE {timestamp_filter})
        SELECT t1.osm_id,
            t1.change_id as changeset_id,
            t1.values,
            t1.lat,
            t1.lon,
            t2.created_at,
            ARRAY_TO_STRING(ARRAY_AGG(t1.unnest_status), ',') AS issues
            FROM t1, t2 WHERE t1.change_id = t2.id
            {filter_hashtags}
            AND unnest_status in ({issue_types})
            GROUP BY t1.osm_id, t1.values, t1.lat, t1.lon, t2.created_at, t1.change_id;
    """

    return query

def generate_data_quality_hashtag_reports_summary(cur, params):
    if params.hashtags is not None and len(params.hashtags) > 0:
        filter_hashtags = ", ".join(["%s"] * len(params.hashtags))
        filter_hashtags = cur.mogrify(
            sql.SQL(filter_hashtags), params.hashtags).decode()
        filter_hashtags = f"AND unnest_hashtags in ({filter_hashtags})"
    else:
        filter_hashtags = ""

    if params.geometry is not None:
        geometry_dump = dumps(dict(params.geometry))
        geom_filter = f"WHERE ST_CONTAINS(ST_GEOMFROMGEOJSON('{geometry_dump}'), location)"
    else:
        geom_filter = ""

    issue_types = ", ".join(["%s"] * len(params.issue_type))
    issue_types_str = [i for i in params.issue_type]
    issue_types = cur.mogrify(sql.SQL(issue_types), issue_types_str).decode()

    timestamp_filter = cur.mogrify(sql.SQL(
        "created_at BETWEEN %s AND %s"), (params.from_timestamp, params.to_timestamp)).decode()

    query = f"""
        WITH t1 AS (
            SELECT source, change_id, unnest(status) AS unnest_status, unnest(values) as unnest_values
            from validation {geom_filter}
        ),
        t2 AS (
            SELECT id, unnest(hashtags) AS unnest_hashtags
            from changesets
            WHERE {timestamp_filter}
        )
        SELECT
            t1.unnest_values as value, t1.source,
            count(t1.unnest_values) as count
            FROM t1, t2 WHERE
            t1.change_id = t2.id
            {filter_hashtags}
            and unnest_values is not null
            AND unnest_status in ({issue_types})
            group by t1.unnest_values, t1.source
            order by count desc;
    """
    return query

def create_hashtagfilter_underpass(hashtags, columnname, project_ids = []):
    """Generates hashtag filter query on the basis of list of hastags."""
    
    hashtag_filter_values = [
        *[f"hotosm-project-{i}" if project_ids is not None else '' for i in project_ids],
        *[f"{i}" for i in hashtags],
    ]

    hashtag_filters = []
    for i in hashtag_filter_values:
        if columnname =="username":
            hashtag_filters.append(f"""'{i}'={columnname}""")
        else:
            hashtag_filters.append(f"""'{i}'=ANY({columnname})""")

    join_query = " OR ".join(hashtag_filters)
    returnquery = f"""{join_query}"""

    return returnquery


def generate_data_quality_TM_query(params):
    '''returns data quality TM query with filters and parameteres provided'''
    # print(params)
    hashtag_add_on = "hotosm-project-"
    if "all" in params.issue_types:
        issue_types = ['badvalue', 'badgeom']
    else:
        issue_types = []
        for p in params.issue_types:
            issue_types.append(str(p))

    change_ids = []
    for p in params.project_ids:
        change_ids.append(hashtag_add_on + str(p))

    hashtagfilter = create_hashtagfilter_underpass(change_ids, "hashtags")
    status_filter = create_hashtagfilter_underpass(issue_types, "status")
    '''Geojson output query for pydantic model'''
    # query1 = """
    #     select '{ "type": "Feature","properties": {   "Osm_id": ' || osm_id ||',"Changeset_id":  ' || change_id ||',"Changeset_timestamp": "' || timestamp ||'","Issue_type": "' || cast(status as text) ||'"},"geometry": ' || ST_AsGeoJSON(location)||'}'
    #     FROM validation
    #     WHERE   status IN (%s) AND
    #             change_id IN (%s)
    # """ % (issue_types, change_ids)
    '''Normal Query to feed our OUTPUT Class '''
    query = f"""   with t1 as (
        select id
                From changesets
                WHERE
                  {hashtagfilter}
            ),
        t2 AS (
             SELECT osm_id as Osm_id,
                change_id as Changeset_id,
                timestamp::text as Changeset_timestamp,
                status::text as Issue_type,
                ST_X(location::geometry) as lng,
                ST_Y(location::geometry) as lat

        FROM validation join t1 on change_id = t1.id
        WHERE
        {status_filter}
                )
        select *
        from t2
        """
    return query


def generate_data_quality_username_query(params, cur):
    '''returns data quality username query with filters and parameteres provided'''
    # print(params)
    if ('all' in params.issue_types) is False:
        issue_types = ", ".join(["%s"] * len(params.issue_types))
        issue_types_str = [i for i in params.issue_types]
        issue_types = cur.mogrify(
            sql.SQL(issue_types), issue_types_str).decode()
        issue_type_filter = f"""and unnest_status in ({issue_types})"""

    else:
        issue_type_filter = ""

    if params.hashtags is not None and len(params.hashtags) > 0:
        hashtag_filt = create_hashtagfilter_underpass(
            params.hashtags, "hashtags")
        filter_hashtags = f""" and {hashtag_filt}"""
    else:
        filter_hashtags = ""
    osm_usernames = []
    for p in params.osm_usernames:
        osm_usernames.append(p)

    username_filter = create_hashtagfilter_underpass(osm_usernames, "username")

    query = f"""with t1 as (
        select
            id,
            username as username
        from
            users
        where
            {username_filter} ),
        t2 as (
        select
            osm_id,
            change_id,
            st_x(location) as lat,
            st_y(location) as lon,
            unnest(status) as unnest_status
        from
            validation,
            t1
        where
            user_id = t1.id),
        t3 as (
        select
            id,
            created_at
        from
            changesets
        where
            (created_at between '{params.from_timestamp}' and  '{params.to_timestamp}'){filter_hashtags} )
        select
            t2.osm_id as Osm_id ,
            t2.change_id as Changeset_id,
            t3.created_at as Changeset_timestamp,
            ARRAY_TO_STRING(ARRAY_AGG(t2.unnest_status), ',') as Issue_type,
            t1.username as username,
            t2.lat,
            t2.lon as lng
        from
            t1,
            t2,
            t3
        where
            t2.change_id = t3.id
            {issue_type_filter}
        group by
            t2.osm_id,
            t1.username,
            t2.lat,
            t2.lon,
            t3.created_at,
            t2.change_id;"""
    # print(query)
    return query


def generate_mapathon_summary_underpass_query(params, cur):
    """Generates mapathon query from underpass"""
    projectid_hashtag_add_on = "hotosm-project-"
    change_ids = []
    for p in params.project_ids:
        change_ids.append(projectid_hashtag_add_on + str(p))

    projectidfilter = create_hashtagfilter_underpass(change_ids, "hashtags")
    hashtags = []
    for p in params.hashtags:
        hashtags.append(str(p))
    hashtagfilter = create_hashtagfilter_underpass(hashtags, "hashtags")
    timestamp_filter = create_timestamp_filter_query(
        "created_at", params.from_timestamp, params.to_timestamp, cur)

    base_where_query = f"""where  ({timestamp_filter}) """
    if hashtagfilter != '' and projectidfilter != '':
        base_where_query += f"""AND ({hashtagfilter} OR {projectidfilter})"""
    elif hashtagfilter == '' and projectidfilter != '':
        base_where_query += f"""AND ({projectidfilter})"""
    else:
        base_where_query += f"""AND ({hashtagfilter})"""
    summary_query = f"""with t1 as (
        select  *
        from changesets
        {base_where_query})
        ,
        t2 as (
        select (each(added)).key as feature , (each(added)).value::Integer as count, 'create'::text as action
        from t1
        union all
        select  (each(modified)).key as feature , (each(modified)).value::Integer as count, 'modify'::text as action
        from t1
        )
        select feature,action ,sum(count) as count
        from t2
        group by feature ,action
        order by count desc """
    total_contributor_query = f"""select  COUNT(distinct user_id) as contributors_count
        from changesets
        {base_where_query}
        """
    # print(summary_query)
    # print("\n")
    # print(total_contributor_query)

    return summary_query, total_contributor_query



def create_changeset_query_underpass(params, conn, cur):
    '''returns the changeset query from Underpass'''

    hashtag_filter=create_hashtagfilter_underpass(params.hashtags, "hashtags", params.project_ids)
    timestamp_filter=create_timestamp_filter_query("created_at",params.from_timestamp, params.to_timestamp,cur)

    changeset_query = f"""
                with t1 as (
                select  *
                from changesets c
                join users u
                on u.id  = c.user_id
                where {hashtag_filter}
                and {timestamp_filter}
        ) ,t2 as (
                select (each(added)).key as feature , (each(added)).value::Integer as count, 'create'::text as action, username, user_id, editor
                from t1
                union all
                select  (each(modified)).key as feature , (each(modified)).value::Integer as count, 'modify'::text as action, username, user_id, editor
                from t1
        )
        select feature,action ,sum(count) as count, username, user_id, array_agg(distinct(editor)) as editors
        from t2
        group by feature ,action, username, user_id
    """
    return changeset_query, hashtag_filter, timestamp_filter

def create_users_contributions_query_underpass(params, conn, cur):
    '''returns the changeset query from Underpass'''

    hashtag_filter=create_hashtagfilter_underpass(params.hashtags, "hashtags", params.project_ids)
    timestamp_filter=create_timestamp_filter_query("created_at",params.from_timestamp, params.to_timestamp,cur)

    contributors_query = f"""
        with t1 as (
        select  *
        from changesets c
        join users u
		on u.id  = c.user_id
		where {hashtag_filter}
		and {timestamp_filter}
        ) ,t2 as (
                select sum((added->'building')::numeric) as added_buildings, sum((modified->'building')::numeric) as modified_buildings, user_id, username, string_agg(distinct (editor)::text, ',') as editors
                from t1
                group by user_id, username
        )
        select user_id, username, (coalesce(added_buildings, 0) + coalesce(modified_buildings, 0)) as total_buildings, editors
        from t2
        group by user_id, total_buildings ,username, editors
    """
    return contributors_query


def generate_training_organisations_query():
    """Generates query for listing out all the organisations listed in training table from underpass
    """
    query = """select oid as id ,name
            from organizations
            order by oid """
    return query


def generate_filter_training_query(params):
    base_filter = []

    if params.oid:
        query = f"""(organization = {params.oid})"""
        base_filter.append(query)

    if params.topic_type:
        topic_type_filter = []
        for value in params.topic_type:
            query = f"""topictype = '{value}'"""
            topic_type_filter.append(query)
        join_query = " OR ".join(topic_type_filter)
        base_filter.append(f"""({join_query})""")

    if params.event_type:
        query = f"""(eventtype = '{params.event_type}')"""
        base_filter.append(query)

    if params.from_datestamp and params.to_datestamp:
        timestamp_query = f"""( date BETWEEN '{params.from_datestamp}'::date AND '{params.to_datestamp}'::date )"""
        base_filter.append(timestamp_query)

    if params.from_datestamp is not None and params.to_datestamp is None:
        timestamp_query = f"""( date >= '{params.from_datestamp}'::date )"""
        base_filter.append(timestamp_query)

    if params.to_datestamp is not None and params.from_datestamp is None:
        timestamp_query = f"""( date <= '{params.to_datestamp}'::date )"""
        base_filter.append(timestamp_query)

    filter_query = " AND ".join(base_filter)
    # print(filter_query)
    return filter_query


def generate_training_query(filter_query):
    base_query = """select * from training """
    if filter_query:
        base_query += f"""WHERE {filter_query}"""
    return base_query


def generate_organization_hashtag_reports(cur, params):
    hashtags = []
    for p in params.hashtags:
        hashtags.append("name = '" + str(p.strip()).lower() + "'")
    filter_hashtags = " or ".join(hashtags)
    # filter_hashtags = cur.mogrify(sql.SQL(filter_hashtags), params.hashtags).decode()
    t2_query = f"""select name as hashtag, type as frequency , start_date , end_date , total_new_buildings , total_uq_contributors as total_unique_contributors , total_new_road_m as total_new_road_meters,
            total_new_amenity as total_new_amenities, total_new_places as total_new_places
            from hashtag_stats join t1 on hashtag_id=t1.id
            where type='{params.frequency}'"""
    # month_time = """0:00:00"""
    # week_time = """12:00:00"""
    if params.end_date is not None or params.start_date is not None:
        timestamp = []
        time = f"""{"12" if params.frequency is Frequency.WEEKLY.value else "00" }"""
        if params.start_date:
            timestamp.append(
                f"""start_date >= '{params.start_date}T{time}:00:00.000'::timestamp""")
        if params.end_date:
            timestamp.append(
                f"""end_date <= '{params.end_date}T{time}:00:00.000'::timestamp""")
        filter_timestamp = " and ".join(timestamp)
        t2_query += f""" and {filter_timestamp}"""
    query = f"""with t1 as (
            select id, name
            from hashtag
            where {filter_hashtags}
            ),
            t2 as (
                {t2_query}
            )
            select *
            from t2
            order by hashtag"""
    # print(query)
    return query


def generate_tm_validators_stats_query(cur, params):
    stmt = """with t0 as (
        select
            id as p_id,
            case
                when status = 0
                        then 'ARCHIVED'
                when status = 1
                        then 'PUBLISHED'
                when status = 2 then 'DRAFT'
            end status,
            total_tasks,
            tasks_mapped,
            tasks_validated,
            organisation_id,
            country
        from projects
        where date_part('year', created) = %s"""

    sub_query = cur.mogrify(sql.SQL(stmt), (params.year,)).decode()
    status_subset = ""
    organisation_subset = ""
    country_subset = ""
    if params.status:
        status_subset = f""" and status ={params.status}"""
    if params.organisation:
        organisation_list = [
            f"""organisation_id = {id}""" for id in params.organisation]
        organisation_join = " or ".join(organisation_list)
        organisation_subset = f""" and ({organisation_join})"""
    if params.country:
        country_subset = f""" and '{params.country}' ~~* any(country)"""

    query = f"""{sub_query}{status_subset}{organisation_subset}{country_subset}
        order by p_id
            )
        ,t1 as (
            select
                validated_by as user_id,
                project_id,
                case
                    when validated_by  is null
                            then 0
                    else count(distinct id)
                end cnt
            from
                tasks , t0
            where
                project_id = t0.p_id
            group by
                user_id,
                project_id
            order by
                project_id
                )
        select
            coalesce(t1.user_id, 0) as user_id,
            coalesce(u.username, 'N/A') as username,
            case
                when u.mapping_level = 1
                                then 'BEGINNER'
                when u.mapping_level = 2
                                then 'INTERMEDIATE'
                when u.mapping_level = 3 then 'ADVANCED'
            end  mapping_level,
            p.p_id as project_id,
            coalesce(t1.cnt, 0) as cnt,
            p.status as project_status,
            coalesce(o.name,'N/A') as organisation_name,
            p.total_tasks,
            p.tasks_mapped,
            p.tasks_validated,
            unnest(p.country) as country
        from
            t0 as p
        left join t1
            on
            t1.project_id = p.p_id
        left join users as u
            on
            u.id = t1.user_id
        left join organisations as o
            on
            o.id = p.organisation_id
        order by
            u.username,
            t1.project_id"""

    return query


def generate_tm_teams_list():
    query = """with vt AS (SELECT distinct team_id as id from project_teams where role = 1 order by id),
            mu AS (SELECT tm.team_id, ARRAY_AGG(users.username) AS managers from team_members AS tm, vt, users WHERE users.id = tm.user_id AND tm.team_id = vt.id AND tm.function = 1 GROUP BY tm.team_id),
            uc AS (SELECT tm.team_id, count(tm.user_id) AS members_count from team_members AS tm, vt WHERE tm.team_id = vt.id GROUP BY tm.team_id)
            SELECT t.id, t.organisation_id, orgs.name AS organisation_name, t.name AS team_name, mu.managers, uc.members_count from teams AS t, mu, uc, organisations AS orgs where orgs.id = t.organisation_id AND t.id = mu.team_id AND t.id = uc.team_id"""

    return query


def generate_list_teams_metadata(team_id):
    sub_query = ""
    if team_id:
        sub_query = f"""and team_id = {team_id}"""
    query = f"""
        with vt AS (SELECT distinct team_id as id from project_teams where role = 1 {sub_query} order by id),
        m AS (SELECT tm.team_id, tm.user_id, users.username, tm.function FROM team_members AS tm, vt, users WHERE users.id = tm.user_id AND tm.team_id = vt.id)
        SELECT m.team_id AS team_id,
            t.name AS team_name,
            orgs.id AS organisation_id,
            orgs.name AS organisation_name,
            m.user_id,
            m.username,
            m.function from m, teams as t, organisations as orgs
        where
            orgs.id = t.organisation_id AND
            t.id = m.team_id
        ORDER BY team_id, function, username;
    """

    return query

def check_last_updated_changesets():
    query = """SELECT (NOW() - MAX(updated_at)) AS "last_updated" FROM public.changesets;"""
    return query

def check_last_updated_validation():
    query = """SELECT (NOW() - MAX(timestamp)) AS "last_updated" FROM public.validation;"""
    return query
