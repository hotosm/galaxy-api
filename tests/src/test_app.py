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

from src.galaxy import app
import testing.postgresql
from src.galaxy.validation import models as mapathon_validation
from src.galaxy.query_builder import builder as mapathon_query_builder
from src.galaxy.query_builder.builder import check_last_updated_changesets, check_last_updated_validation, generate_organization_hashtag_reports, create_UserStats_get_statistics_query, create_userstats_get_statistics_with_hashtags_query, generate_data_quality_TM_query, generate_data_quality_username_query, generate_data_quality_hashtag_reports
from src.galaxy.validation.models import OrganizationHashtagParams, UserStatsParams, DataQuality_TM_RequestParams, DataQuality_username_RequestParams, DataQualityHashtagParams
import os.path

# Reference to testing.postgresql db instance
postgresql = None

# Connection to database and query running class from our src.galaxy module

database = None
filepath=None

# Generate Postgresql class which shares the generated database so that we could use it in all test function (now we don't need to create db everytime whenever the test runs)
Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

global test_param
test_param = {
    "project_ids": [
        11224, 10042, 9906, 1381, 11203, 10681, 8055, 8732, 11193, 7305,
        11210, 10985, 10988, 11190, 6658, 5644, 10913, 6495, 4229
    ],
    "fromTimestamp":
        "2021-08-27T9:00:00",
        "toTimestamp":
        "2021-08-27T11:00:00",
        "hashtags": ["mapandchathour2021"]
}


def slurp(path):
    """ Reads and returns the entire contents of a file """
    with open(path, 'r') as f:
        return f.read()


def setup_module(module):
    """ Module level set-up called once before any tests in this file are
    executed.  shares a temporary database created in Postgresql and sets it up """

    print('*****SETUP*****')
    global postgresql, database, con, cur, db_dict

    postgresql = Postgresql()
    # passing test credentials to our osm_stat database class for connection
    """ Default credentials : {'port': **dynamic everytime **, 'host': '127.0.0.1', 'user': 'postgres', 'database': 'test'}"""
    db_dict = postgresql.dsn()
    database = app.Database(db_dict)
    # To Ensure the database is in a known state before calling the function we're testing
    con, cur = database.connect()
    # Map of database connection parameters passed to the app we're testing
    print(postgresql.dsn())


def teardown_module(module):
    """ Called after all of the tests in this file have been executed to close
    the database connection and destroy the temporary database """

    print('******TEARDOWN******')
    # close our database connection to avoid memory leaks i.e. available feature in our database class
    database.close_conn()
    # clear cached database at end of tests
    Postgresql.clear_cache()
    if filepath:
        if os.path.isfile(filepath) is True:
            os.remove(filepath)

def test_data_quality_hashtags_query_builder():
    # No geometry, with hashtags.
    test_params = {
        "hashtags": ["missingmaps"],
        "issueType": ["badgeom"],
        "outputType": "geojson",
        "fromTimestamp": "2020-12-10T00:00:00",
        "toTimestamp": "2020-12-11T00:00:00"
    }

    test_data_quality_hashtags_query = "\n        WITH t1 AS (SELECT osm_id, change_id, values, st_x(location) AS lat, st_y(location) AS lon, unnest(status) AS unnest_status from validation ),\n        t2 AS (SELECT id, created_at, unnest(hashtags) AS unnest_hashtags from changesets WHERE created_at BETWEEN '2020-12-10T00:00:00'::timestamp AND '2020-12-11T00:00:00'::timestamp)\n        SELECT t1.osm_id,\n            t1.change_id as changeset_id,\n            t1.values,\n            t1.lat,\n            t1.lon,\n            t2.created_at,\n            ARRAY_TO_STRING(ARRAY_AGG(t1.unnest_status), ',') AS issues\n            FROM t1, t2 WHERE t1.change_id = t2.id\n            AND unnest_hashtags in ('missingmaps')\n            AND unnest_status in ('badgeom')\n            GROUP BY t1.osm_id, t1.values, t1.lat, t1.lon, t2.created_at, t1.change_id;\n    "

    params = DataQualityHashtagParams(**test_params)
    query = generate_data_quality_hashtag_reports(cur, params)

    assert query == test_data_quality_hashtags_query

    # Test geometry, no hashtags.
    test_params = {
        "fromTimestamp": "2020-12-10T00:00:00",
        "toTimestamp": "2020-12-11T00:00:00",
        "issueType": [
            "badgeom"
        ],
        "outputType": "geojson",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -74.80708971619606,
                        11.002032789290594
                    ],
                    [
                        -74.80621799826622,
                        11.002032789290594
                    ],
                    [
                        -74.80621799826622,
                        11.00265678856572
                    ],
                    [
                        -74.80708971619606,
                        11.00265678856572
                    ],
                    [
                        -74.80708971619606,
                        11.002032789290594
                    ]
                ]
            ]
        }
    }

    test_data_quality_hashtags_query_no_hashtags = '\n        WITH t1 AS (SELECT osm_id, change_id, values, st_x(location) AS lat, st_y(location) AS lon, unnest(status) AS unnest_status from validation WHERE ST_CONTAINS(ST_GEOMFROMGEOJSON(\'{"coordinates": [[[-74.80708971619606, 11.002032789290594], [-74.80621799826622, 11.002032789290594], [-74.80621799826622, 11.00265678856572], [-74.80708971619606, 11.00265678856572], [-74.80708971619606, 11.002032789290594]]], "type": "Polygon"}\'), location)),\n        t2 AS (SELECT id, created_at, unnest(hashtags) AS unnest_hashtags from changesets WHERE created_at BETWEEN \'2020-12-10T00:00:00\'::timestamp AND \'2020-12-11T00:00:00\'::timestamp)\n        SELECT t1.osm_id,\n            t1.change_id as changeset_id,\n            t1.values,\n            t1.lat,\n            t1.lon,\n            t2.created_at,\n            ARRAY_TO_STRING(ARRAY_AGG(t1.unnest_status), \',\') AS issues\n            FROM t1, t2 WHERE t1.change_id = t2.id\n            \n            AND unnest_status in (\'badgeom\')\n            GROUP BY t1.osm_id, t1.values, t1.lat, t1.lon, t2.created_at, t1.change_id;\n    '
    params = DataQualityHashtagParams(**test_params)
    query = generate_data_quality_hashtag_reports(cur, params)

    assert query == test_data_quality_hashtags_query_no_hashtags

def test_mapathon_users_contributors_mapathon_query_builder():
    default_users_contributors_query = '\n        with t0 as (\n        SELECT user_id, array_agg(distinct (editor)) as editor\n            FROM changesets c\n            WHERE added->\'building\' is not null\n            and created_at BETWEEN \'2021-08-27T09:00:00\' AND \'2021-08-27T11:00:00\'\n            group by user_id\n        ),\n        t1 as (\n            SELECT added->\'building\' as added_buildings, user_id, username\n            FROM changesets c\n            INNER JOIN users u ON u.id = c.user_id\n            WHERE added->\'building\' is not null\n            and created_at BETWEEN 2021-08-27T09:00:00\' AND \'2021-08-27T11:00:00\'\n            group by user_id, username, added_buildings\n        )\n        select t1.user_id, username, sum(added_buildings::numeric) as total_buildings, editor from t1\n        inner join t0 on t0.user_id = t1.user_id\n        group by t1.user_id, username, editor;\n    '
    params = mapathon_validation.MapathonRequestParams(**test_param)
    changeset_query, _, _ = mapathon_query_builder.create_changeset_query(params, con,
                                                                          cur)
    result_users_contributors_query = mapathon_query_builder.create_users_contributions_query(
        params, changeset_query)
    assert result_users_contributors_query == default_users_contributors_query


def test_mapathon_users_tasks_mapped_and_validated_query_builder():
    default_tasks_mapped_query = '\n        SELECT th.user_id, COUNT(th.task_id) as tasks_mapped\n            FROM PUBLIC.task_history th\n            WHERE th.action_text = \'MAPPED\'\n            AND th.action_date BETWEEN \'2021-08-27 09:00:00\' AND \'2021-08-27 11:00:00\'\n            AND th.project_id IN (11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229)\n            GROUP BY th.user_id;\n    '
    default_tasks_validated_query = '\n        SELECT th.user_id, COUNT(th.task_id) as tasks_validated\n            FROM PUBLIC.task_history th\n            WHERE th.action_text = \'VALIDATED\'\n            AND th.action_date BETWEEN \'2021-08-27 09:00:00\' AND \'2021-08-27 11:00:00\'\n            AND th.project_id IN (11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229)\n            GROUP BY th.user_id;\n    '
    params = mapathon_validation.MapathonRequestParams(**test_param)
    result_tasks_mapped_query, result_tasks_validated_query = mapathon_query_builder.create_user_tasks_mapped_and_validated_query(
        params.project_ids, params.from_timestamp, params.to_timestamp)

    assert result_tasks_mapped_query == default_tasks_mapped_query
    assert result_tasks_validated_query == default_tasks_validated_query


def test_mapathon_users_time_spent_mapping_and_validating_query_builder():
    default_time_mapping_query = '\n        SELECT user_id, SUM(CAST(TO_TIMESTAMP(action_text, \'HH24:MI:SS\') AS TIME)) AS time_spent_mapping\n        FROM public.task_history\n        WHERE\n            (action = \'LOCKED_FOR_MAPPING\'\n            OR action = \'AUTO_UNLOCKED_FOR_MAPPING\')\n            AND action_date BETWEEN \'2021-08-27 09:00:00\' AND \'2021-08-27 11:00:00\'\n            AND project_id IN (11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229)\n        GROUP BY user_id;\n    '
    default_time_validating_query = '\n        SELECT user_id, SUM(CAST(TO_TIMESTAMP(action_text, \'HH24:MI:SS\') AS TIME)) AS time_spent_validating\n        FROM public.task_history\n        WHERE action = \'LOCKED_FOR_VALIDATION\'\n            AND action_date BETWEEN \'2021-08-27 09:00:00\' AND \'2021-08-27 11:00:00\'\n            AND project_id IN (11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229)\n        GROUP BY user_id;\n    '
    params = mapathon_validation.MapathonRequestParams(**test_param)
    result_time_mapping_query, result_time_validating_query = mapathon_query_builder.create_user_time_spent_mapping_and_validating_query(
        params.project_ids, params.from_timestamp, params.to_timestamp)

    assert result_time_mapping_query == default_time_mapping_query
    assert result_time_validating_query == default_time_validating_query


def test_data_quality_TM_query():
    """Function to test data quality TM query generator of Data Quality Class """
    data_quality_params = {
        "project_ids": [
            9928, 4730, 5663
        ],
        "issue_types": ["badgeom", "badvalue"],
        "output_type": "geojson"
    }
    validated_params = DataQuality_TM_RequestParams(**data_quality_params)
    expected_result = """   with t1 as (\n        select id\n                From changesets\n                WHERE\n                  'hotosm-project-9928'=ANY(hashtags) OR 'hotosm-project-4730'=ANY(hashtags) OR 'hotosm-project-5663'=ANY(hashtags)\n            ),\n        t2 AS (\n             SELECT osm_id as Osm_id,\n                change_id as Changeset_id,\n                timestamp::text as Changeset_timestamp,\n                status::text as Issue_type,\n                ST_X(location::geometry) as lng,\n                ST_Y(location::geometry) as lat\n\n        FROM validation join t1 on change_id = t1.id\n        WHERE\n        'badgeom'=ANY(status) OR 'badvalue'=ANY(status)\n                )\n        select *\n        from t2\n        """
    query_result = generate_data_quality_TM_query(validated_params)
    assert query_result == expected_result


def test_data_quality_username_query():
    """Function to test data quality username query generator of Data Quality Class """
    data_quality_params = {
        "fromTimestamp": "2021-07-01T00:30:00.000",
        "toTimestamp": "2021-07-02T00:15:00.000",
        "osmUsernames": [
            "Fadlilaa IRM-ED", "Bert Araali"
        ],
        "issueTypes": [
            "badgeom"
        ],
        "outputType": "geojson"
    }
    hashtag_params = {"fromTimestamp": "2022-04-25T18:15:00.994Z", "toTimestamp": "2022-04-30T18:14:59.994Z",
                      "osmUsernames": ["Riyadi IRM-ED"], "issueTypes": ["all"], "hashtags": ["Indonesia"], "outputType": "geojson"}

    validated_params = DataQuality_username_RequestParams(
        **data_quality_params)
    validated_hashtag_params = DataQuality_username_RequestParams(
        **hashtag_params)

    expected_result = """with t1 as (
        select
            id,
            username as username
        from
            users
        where
            'Fadlilaa IRM-ED'=username OR 'Bert Araali'=username ),
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
            (created_at between '2021-07-01 00:30:00' and  '2021-07-02 00:15:00') )
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
            and unnest_status in ('badgeom')
        group by
            t2.osm_id,
            t1.username,
            t2.lat,
            t2.lon,
            t3.created_at,
            t2.change_id;"""
    expected_hashtag_result = """with t1 as (\n        select\n            id,\n            username as username\n        from\n            users\n        where\n            'Riyadi IRM-ED'=username ),\n        t2 as (\n        select\n            osm_id,\n            change_id,\n            st_x(location) as lat,\n            st_y(location) as lon,\n            unnest(status) as unnest_status\n        from\n            validation,\n            t1\n        where\n            user_id = t1.id),\n        t3 as (\n        select\n            id,\n            created_at\n        from\n            changesets\n        where\n            (created_at between '2022-04-25 18:15:00.994000+00:00' and  '2022-04-30 18:14:59.994000+00:00') and 'Indonesia'=ANY(hashtags) )\n        select\n            t2.osm_id as Osm_id ,\n            t2.change_id as Changeset_id,\n            t3.created_at as Changeset_timestamp,\n            ARRAY_TO_STRING(ARRAY_AGG(t2.unnest_status), ',') as Issue_type,\n            t1.username as username,\n            t2.lat,\n            t2.lon as lng\n        from\n            t1,\n            t2,\n            t3\n        where\n            t2.change_id = t3.id\n            \n        group by\n            t2.osm_id,\n            t1.username,\n            t2.lat,\n            t2.lon,\n            t3.created_at,\n            t2.change_id;"""

    query_result = generate_data_quality_username_query(validated_params, cur)
    assert query_result.encode('utf-8') == expected_result.encode('utf-8')

    query_hashtag_result = generate_data_quality_username_query(
        validated_hashtag_params, cur)
    assert query_hashtag_result.encode(
        'utf-8') == expected_hashtag_result.encode('utf-8')


def test_userstats_get_statistics_with_hashtags_query():
    """Function to  test userstats class's get_statistics query generator """
    test_params = {
        "userId": 11593794,
        "fromTimestamp": "2021-08-27T9:00:00",
        "toTimestamp": "2021-08-27T11:00:00",
        "hashtags": [
            "mapandchathour2021"
        ],
        "projectIds": [11224, 10042, 9906, 1381, 11203, 10681, 8055, 8732, 11193, 7305, 11210,
                       10985, 10988, 11190, 6658, 5644, 10913, 6495, 4229]
    }
    validated_params = UserStatsParams(**test_params)
    expected_result = "\n    SELECT\n    sum((added->\'building\')::numeric) AS added_buildings,\n    sum((modified->\'building\')::numeric) AS modified_buildings,\n    sum((added->\'highway\')::numeric) AS added_highway,\n    sum((modified->\'highway\')::numeric) AS modified_highway,\n    sum((added->\'highway_km\')::numeric) AS added_highway_km,\n    sum((modified->\'highway_km\')::numeric) AS modified_highway_km\n    FROM changesets c\n    WHERE c.\"created_at\" between \'2021-08-27T09:00:00\'::timestamp AND \'2021-08-27T11:00:00\'::timestamp\n    AND user_id = 11593794\n    AND \'mapandchathour2021\'=ANY(hashtags);\n    "
    query_result = create_userstats_get_statistics_with_hashtags_query(
        validated_params, con, cur)
    assert query_result.encode('utf-8') == expected_result.encode('utf-8')


def test_userstats_get_statistics_query():
    """Function to  test userstats class's get_statistics query generator """
    test_params = {
        "userId": 11593794,
        "fromTimestamp": "2021-08-27T9:00:00",
        "toTimestamp": "2021-08-27T11:00:00",
        "hashtags": [
        ],
        "projectIds": [11224]
    }
    validated_params = UserStatsParams(**test_params)
    expected_result = "\n    SELECT\n    sum((added->'building')::numeric) AS added_buildings,\n    sum((modified->'building')::numeric) AS modified_buildings,\n    sum((added->'highway')::numeric) AS added_highway,\n    sum((modified->'highway')::numeric) AS modified_highway,\n    sum((added->'highway_km')::numeric) AS added_highway_km\n    sum((modified->'highway_km')::numeric) AS modified_highway_km\n    FROM changesets\n    WHERE created_at BETWEEN '2021-08-27T09:00:00'::timestamp AND '2021-08-27T11:00:00'::timestamp\n    AND user_id = 11593794;\n    "
    query_result = create_UserStats_get_statistics_query(
        validated_params, con, cur)
    assert query_result == expected_result.encode('utf-8')


def test_organization_hashtag_weekly_query():
    """[Function to test ogranization hashtag api query generation]
    """
    # for weekly stat
    test_params = {
        "hashtag": "msf",
        "frequency": "w",
        "outputType": "json",
        "startDate": "2022-10-20",
        "endDate": "2022-12-22"
    }
    validated_params = OrganizationHashtagParams(**test_params)
    expected_query = '\n    with t1 as (\n        select * from changesets where\n        closed_at BETWEEN \'2022-10-20\' AND \'2022-12-22\'\n    )\n    SELECT \n        date_trunc(\'week\', closed_at::date) AS "startDate",\n        date_trunc(\'week\', closed_at::date) + interval \'1 WEEK\' AS "endDate",\n        COUNT(distinct (user_id)) AS "totalUniqueContributors",\n        coalesce(sum((added->\'building\')::numeric), 0) AS "totalNewBuildings",\n        coalesce(sum((added->\'amenity\')::numeric), 0) AS "totalNewAmenities",\n        coalesce(sum((added->\'place\')::numeric), 0) AS "totalNewPlaces",\n        coalesce(sum((added->\'highway_km\')::numeric), 0) AS "totalNewRoadKm",\n        \'w\' AS frequency,\n        \'msf\' AS hashtag\n        FROM t1 \n        WHERE \'msf\' = any(hashtags)\n        AND added IS NOT NULL OR modified IS NOT NULL\n        GROUP BY "startDate", "endDate"\n        ORDER BY "startDate" ASC;\n    '
    query_result = generate_organization_hashtag_reports(cur, validated_params)
    assert query_result.encode('utf-8') == expected_query.encode('utf-8')


def test_organization_hashtag_monthly_query():
    # for monthly stat
    month_param = {
        "hashtag": "msf",
        "frequency": "m",
        "outputType": "json",
        "startDate": "2022-01-20",
        "endDate": "2022-12-22"
    }
    validated_params = OrganizationHashtagParams(**month_param)
    expected_query = expected_query = '\n    with t1 as (\n        select * from changesets where\n        closed_at BETWEEN \'2022-01-20\' AND \'2022-12-22\'\n    )\n    SELECT \n        date_trunc(\'month\', closed_at::date) AS "startDate",\n        date_trunc(\'month\', closed_at::date) + interval \'1 MONTH\' AS "endDate",\n        COUNT(distinct (user_id)) AS "totalUniqueContributors",\n        coalesce(sum((added->\'building\')::numeric), 0) AS "totalNewBuildings",\n        coalesce(sum((added->\'amenity\')::numeric), 0) AS "totalNewAmenities",\n        coalesce(sum((added->\'place\')::numeric), 0) AS "totalNewPlaces",\n        coalesce(sum((added->\'highway_km\')::numeric), 0) AS "totalNewRoadKm",\n        \'m\' AS frequency,\n        \'msf\' AS hashtag\n        FROM t1 \n        WHERE \'msf\' = any(hashtags)\n        AND added IS NOT NULL OR modified IS NOT NULL\n        GROUP BY "startDate", "endDate"\n        ORDER BY "startDate" ASC;\n    '
    query_result = generate_organization_hashtag_reports(cur, validated_params)
    assert query_result.encode('utf-8') == expected_query.encode('utf-8')

def test_user_statistics_recency_query():
    expected_insights_query = 'SELECT (NOW() - MAX(updated_at)) AS "last_updated" FROM public.changesets;'
    assert check_last_updated_changesets() == expected_insights_query

def test_user_data_quality_recency_query():
    expected_underpass_query = 'SELECT (NOW() - MAX(timestamp)) AS "last_updated" FROM public.validation;'
    assert check_last_updated_validation() == expected_underpass_query
