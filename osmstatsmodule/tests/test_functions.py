from osm_stats import functions
import testing.postgresql
import pytest
from osm_stats import validation
from osm_stats import query_builder

# Reference to testing.postgresql db instance
postgresql=None

# Connection to database and query running class from our osm_stats module

database=None


# Generate Postgresql class which shares the generated database so that we could use it in all test function (now we don't need to create db everytime whenever the test runs)
Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

def setup_module(module):
    """ Module level set-up called once before any tests in this file are
    executed.  shares a temporary database created in Postgresql and sets it up """

    print('*****SETUP*****')
    global postgresql,database,con,cur

    postgresql = Postgresql()
    # passing test credentials to our osm_stat database class for connection 
    """ Default credentials : {'port': **dynamic everytime **, 'host': '127.0.0.1', 'user': 'postgres', 'database': 'test'}"""
    database= functions.Database(postgresql.dsn())
    # To Ensure the database is in a known state before calling the function we're testing
    con,cur=database.connect()
    # Map of database connection parameters passed to the functions we're testing
    print(postgresql.dsn())
 

def teardown_module(module):
    """ Called after all of the tests in this file have been executed to close
    the database connection and destroy the temporary database """

    print('******TEARDOWN******')
    # close our database connection to avoid memory leaks i.e. available feature in our database class 
    database.close_conn()
    # clear cached database at end of tests
    Postgresql.clear_cache()

def test_db_create(): 
    createtable=f""" CREATE TABLE test_table (id int, value varchar(256))"""
    print(database.executequery(createtable))

def test_db_insert():
    insertvalue=f""" INSERT INTO test_table values(1, 'hello'), (2, 'namaste')"""
    print(database.executequery(insertvalue))

def test_db_query():
    query=f""" SELECT * from test_table;"""
    result=database.executequery(query)
    print(result)
    # validating the query result either it is right or not 
    assert result == [[1, 'hello'], [2, 'namaste']]

def test_mapathon_osm_history_query_builder():
    test_param={
        "project_ids": [11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229],
        "fromTimestamp": "2021-08-27T9:00:00",
        "toTimestamp": "2021-08-27T11:00:00",
        "hashtags": ["mapandchathour2021"]
        }
    default_osm_history_query= '\n    WITH T1 AS(\n    SELECT user_id, id as changeset_id, user_name as username\n    FROM osm_changeset\n    WHERE "created_at" between \'2021-08-27T09:00:00\'::timestamp AND \'2021-08-27T11:00:00\'::timestamp AND (("tags" -> \'hashtags\') ~~ \'%hotosm-project-11224%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11224%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10042%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10042%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-9906%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-9906%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-1381%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-1381%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11203%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11203%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10681%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10681%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-8055%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-8055%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-8732%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-8732%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11193%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11193%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-7305%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-7305%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11210%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11210%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10985%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10985%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10988%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10988%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11190%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11190%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-6658%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-6658%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-5644%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-5644%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10913%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10913%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-6495%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-6495%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-4229%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-4229%\' OR ("tags" -> \'hashtags\') ~~ \'%mapandchathour2021%\' OR ("tags" -> \'comment\') ~~ \'%mapandchathour2021%\')\n    )\n    SELECT (each(tags)).key AS feature, action, count(distinct id) AS count FROM osm_element_history AS t2, t1\n    WHERE t1.changeset_id = t2.changeset\n    GROUP BY feature, action ORDER BY count DESC\n    '
    params=validation.MapathonRequestParams(**test_param)
    changeset_query, hashtag_filter, timestamp_filter = query_builder.create_changeset_query(params, con, cur )
    result_osm_history_query = query_builder.create_osm_history_query(changeset_query, with_username=False)
    assert result_osm_history_query == default_osm_history_query

def test_mapathon_total_contributor_query_builder():
    test_param={
        "project_ids": [11224,10042,9906,1381,11203,10681,8055,8732,11193,7305,11210,10985,10988,11190,6658,5644,10913,6495,4229],
        "fromTimestamp": "2021-08-27T9:00:00",
        "toTimestamp": "2021-08-27T11:00:00",
        "hashtags": ["mapandchathour2021"]
        }
    default_total_contributor_query= '\n                SELECT COUNT(distinct user_id) as contributors_count\n                FROM osm_changeset\n                WHERE "created_at" between \'2021-08-27T09:00:00\'::timestamp AND \'2021-08-27T11:00:00\'::timestamp AND (("tags" -> \'hashtags\') ~~ \'%hotosm-project-11224%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11224%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10042%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10042%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-9906%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-9906%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-1381%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-1381%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11203%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11203%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10681%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10681%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-8055%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-8055%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-8732%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-8732%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11193%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11193%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-7305%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-7305%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11210%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11210%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10985%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10985%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10988%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10988%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-11190%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-11190%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-6658%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-6658%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-5644%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-5644%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-10913%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-10913%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-6495%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-6495%\' OR ("tags" -> \'hashtags\') ~~ \'%hotosm-project-4229%\' OR ("tags" -> \'comment\') ~~ \'%hotosm-project-4229%\' OR ("tags" -> \'hashtags\') ~~ \'%mapandchathour2021%\' OR ("tags" -> \'comment\') ~~ \'%mapandchathour2021%\')\n            '
    params=validation.MapathonRequestParams(**test_param)
    changeset_query, hashtag_filter, timestamp_filter = query_builder.create_changeset_query(params, con, cur )
    result_total_contributor_query=f"""
                SELECT COUNT(distinct user_id) as contributors_count
                FROM osm_changeset
                WHERE {timestamp_filter} AND ({hashtag_filter})
            """
    assert result_total_contributor_query == default_total_contributor_query


