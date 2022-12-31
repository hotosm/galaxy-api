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
"""Main page contains class for database mapathon and funtion for error printing  """
import sys
from csv import DictWriter
from io import StringIO
from json import loads as json_loads

import pandas
from geojson import Feature, FeatureCollection, Point
from psycopg2 import OperationalError, connect, sql
from psycopg2.extras import DictCursor

from .config import get_db_connection_params
from .config import logger as logging
from .query_builder.builder import (
    check_last_updated_changesets,
    check_last_updated_validation,
    create_changeset_query_underpass,
    create_user_tasks_mapped_and_validated_query,
    create_user_time_spent_mapping_and_validating_query,
    create_users_contributions_query_underpass,
    create_UserStats_get_statistics_query,
    create_userstats_get_statistics_with_hashtags_query,
    generate_data_quality_hashtag_reports,
    generate_data_quality_hashtag_reports_summary,
    generate_data_quality_TM_query,
    generate_data_quality_username_query,
    generate_filter_training_query,
    generate_list_teams_metadata,
    generate_mapathon_summary_underpass_query,
    generate_organization_hashtag_reports,
    generate_tm_teams_list,
    generate_tm_validators_stats_query,
    generate_training_organisations_query,
    generate_training_query,
)
from .validation.models import (
    DataQuality_TM_RequestParams,
    DataQuality_username_RequestParams,
    DataQualityHashtagParams,
    DataRecencyParams,
    List,
    MapathonContributor,
    MapathonDetail,
    MapathonRequestParams,
    MapathonSummary,
    MappedFeature,
    MappedFeatureWithUser,
    MappedTaskStats,
    OrganizationHashtag,
    OrganizationHashtagParams,
    TeamMemberFunction,
    TimeSpentMapping,
    TimeSpentValidating,
    TMUserStats,
    TrainingOrganisations,
    TrainingParams,
    Trainings,
    User,
    UserRole,
    UserStatistics,
    ValidatedTaskStats,
)


def print_psycopg2_exception(err):
    """
    Function that handles and parses Psycopg2 exceptions
    """
    """details_exception"""
    err_type, err_obj, traceback = sys.exc_info()
    line_num = traceback.tb_lineno
    # the connect() error
    print("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print("psycopg2 traceback:", traceback, "-- type:", err_type)
    # psycopg2 extensions.Diagnostics object attribute
    print("\nextensions.Diagnostics:", err.diag)
    # pgcode and pgerror exceptions
    print("pgerror:", err.pgerror)
    print("pgcode:", err.pgcode, "\n")
    raise err


def check_for_json(result_str):
    """Check if the Payload is a JSON document

    Return: bool:
        True in case of success, False otherwise
    """
    try:
        r_json = json_loads(result_str)
        return True, r_json
    except Exception as ex:
        logging.error(ex)
        return False, None


class Database:
    """Database class is used to connect with your database , run query  and get result from it . It has all tests and validation inside class"""

    def __init__(self, db_params):
        """Database class constructor"""

        self.db_params = db_params

    def connect(self):
        """Database class instance method used to connect to database parameters with error printing"""

        try:
            self.conn = connect(**self.db_params)
            self.cur = self.conn.cursor(cursor_factory=DictCursor)
            logging.debug("Database connection has been Successful...")
            return self.conn, self.cur
        except OperationalError as err:
            """pass exception to function"""

            print_psycopg2_exception(err)
            # set the connection to 'None' in case of error
            self.conn = None

    def executequery(self, query):
        """Function to execute query after connection"""
        # Check if the connection was successful
        try:
            if self.conn is not None:
                self.cursor = self.cur
                if query is not None:
                    # catch exception for invalid SQL statement

                    try:
                        logging.debug("Query sent to Database")
                        self.cursor.execute(query)
                        try:
                            result = self.cursor.fetchall()
                            logging.debug("Result fetched from Database")
                            return result
                        except Exception as ex:
                            logging.error(ex)
                            return self.cursor.statusmessage
                    except Exception as err:
                        print_psycopg2_exception(err)
                else:
                    raise ValueError("Query is Null")

                    # rollback the previous transaction before starting another
                    self.conn.rollback()
                # closing  cursor object to avoid memory leaks
                # cursor.close()
                # self.conn.close()
            else:
                print("Database is not connected")
        except Exception as err:
            print("Oops ! You forget to have connection first")
            raise err

    def close_conn(self):
        """function for clossing connection to avoid memory leaks"""

        # Check if the connection was successful
        try:
            if self.conn is not None:
                if self.cur is not None:
                    self.cur.close()
                    self.conn.close()
                    logging.debug("Database Connection closed")
        except Exception as err:
            raise err


class Underpass:
    """This class connects to underpass database and responsible for all the underpass related functionality"""

    def __init__(self, parameters=None):
        self.database = Database(get_db_connection_params("UNDERPASS"))
        # self.database = Database(dict(config.items("UNDERPASS")))
        self.con, self.cur = self.database.connect()
        self.params = parameters

    def get_mapathon_summary_result(self):
        """Get summary result"""
        (
            osm_history_query,
            total_contributor_query,
        ) = generate_mapathon_summary_underpass_query(self.params, self.cur)
        # print(osm_history_query)
        osm_history_result = self.database.executequery(osm_history_query)
        total_contributors_result = self.database.executequery(total_contributor_query)
        return osm_history_result, total_contributors_result

    def all_training_organisations(self):
        """[Resposible for the total organisations result generation]

        Returns:
            [query_result]: [oid,name]
        """
        training_all_organisations_query = generate_training_organisations_query()
        query_result = self.database.executequery(training_all_organisations_query)
        return query_result

    def training_list(self, params):
        """Returns a list of training organizations."""
        filter_training_query = generate_filter_training_query(params)
        training_query = generate_training_query(filter_training_query)
        # print(training_query)
        query_result = self.database.executequery(training_query)
        # print(query_result)
        return query_result

    def get_user_role(self, user_id: int):
        """returns user role for given user id"""
        query = f"select role from users_roles where user_id = {user_id}"
        query_result = self.database.executequery(query)

        if len(query_result) == 0:
            return UserRole.NONE

        role_int = query_result[0]["role"]
        user_role = UserRole(role_int)

        return user_role

    def get_mapathon_detailed_result(self):
        """Functions that returns detailed reports  for mapathon results_dicts"""
        changeset_query, _, _ = create_changeset_query_underpass(
            self.params, self.con, self.cur
        )
        contributors_query = create_users_contributions_query_underpass(
            self.params, self.con, self.cur
        )
        changesets = self.database.executequery(changeset_query)
        contributors = self.database.executequery(contributors_query)
        return changesets, contributors

    def get_osm_last_updated(self):
        """OSM synchronisation"""
        status_query = check_last_updated_changesets()
        result = self.database.executequery(status_query)
        return result[0][0]

    def get_user_data_quality_last_updated(self):
        """Recency of user data quality reports"""
        status_query = check_last_updated_validation()
        result = self.database.executequery(status_query)
        return result[0][0]

    def get_mapathon_statistics_last_updated(self):
        """Recency of mapathon statistics"""
        status_query = check_last_updated_changesets()
        result = self.database.executequery(status_query)
        return result[0][0]

    def get_user_statistics_last_updated(self):
        """Recency of user statistics"""
        status_query = check_last_updated_changesets()
        result = self.database.executequery(status_query)
        return result[0][0]


class TaskingManager:
    """This class connects to the Tasking Manager database and is responsible for all the TM related functionality."""

    def __init__(self, parameters=None):
        self.database = Database(get_db_connection_params("TM"))
        self.con, self.cur = self.database.connect()
        self.params = parameters

    def extract_project_ids(self):
        """Functions that returns project ids"""
        test_hashtag = "hotosm-project-"
        ids = []

        if len(self.params.project_ids) > 0:
            ids.extend(self.params.project_ids)

        if len(self.params.hashtags) > 0:
            for hashtag in self.params.hashtags:
                if test_hashtag in hashtag:
                    if len(hashtag[15:]) > 0:
                        ids.append(hashtag[15:])
        return ids

    def get_tasks_mapped_and_validated_per_user(self):
        """Function reutrns task mapped and validated from TM database"""
        project_ids = self.extract_project_ids()
        if len(project_ids) > 0:
            (
                tasks_mapped_query,
                tasks_validated_query,
            ) = create_user_tasks_mapped_and_validated_query(
                project_ids, self.params.from_timestamp, self.params.to_timestamp
            )
            tasks_mapped_result = self.database.executequery(tasks_mapped_query)
            tasks_validated_result = self.database.executequery(tasks_validated_query)
            return tasks_mapped_result, tasks_validated_result
        return [], []

    def get_time_spent_mapping_and_validating_per_user(self):
        """Functions that returns time spent in the mapping per user."""
        project_ids = self.extract_project_ids()
        if len(project_ids) > 0:
            (
                time_spent_mapping_query,
                time_spent_validating_query,
            ) = create_user_time_spent_mapping_and_validating_query(
                project_ids, self.params.from_timestamp, self.params.to_timestamp
            )
            time_spent_mapping_result = self.database.executequery(
                time_spent_mapping_query
            )
            time_spent_validating_result = self.database.executequery(
                time_spent_validating_query
            )
            return time_spent_mapping_result, time_spent_validating_result
        return [], []

    def get_validators_stats(self):
        """Generate a list of validators for the TM

        Returns:
            [type]: [description]
        """
        query = generate_tm_validators_stats_query(self.cur, self.params)
        print(query)
        result = [dict(r) for r in self.database.executequery(query)]
        if result:
            indexes = ["user_id", "username", "mapping_level"]
            columns = [
                "project_id",
                "country",
                "organisation_name",
                "project_status",
                "total_tasks",
                "tasks_mapped",
                "tasks_validated",
            ]

            df = pandas.DataFrame(result)
            out = (
                pandas.pivot_table(
                    df,
                    values="cnt",
                    index=indexes,
                    columns=columns,
                    aggfunc="sum",
                    margins=True,
                    margins_name="Total",
                    fill_value=0,
                )
                .swaplevel(0, 1)
                .sort_values(by="username", ascending=True)
                .reset_index()
            )
            print(out)

            stream = StringIO()
            out.to_csv(stream)

            return iter(stream.getvalue())
        return None

    def list_teams(self):
        """Functions    that    returns     teams in tasking manager"""
        query = generate_tm_teams_list()
        results_dicts = [dict(r) for r in self.database.executequery(query)]

        stream = StringIO()

        csv_keys: List[str] = list(results_dicts[0].keys())
        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        [writer.writerow(row) for row in results_dicts]

        return iter(stream.getvalue())

    def list_teams_metadata(self, team_id):
        """Functions   that    returns teams metadata for a given team"""
        query = generate_list_teams_metadata(team_id)
        results_dicts = [dict(r) for r in self.database.executequery(query)]

        results_dicts = [
            {**r, "function": TeamMemberFunction(r["function"]).name.lower()}
            for r in results_dicts
        ]

        stream = StringIO()

        csv_keys: List[str] = list(results_dicts[0].keys())
        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        [writer.writerow(row) for row in results_dicts]

        return iter(stream.getvalue())


class Mapathon:
    """Class for mapathon detail report and summary report this is the class that self connects to database and provide you summary and detail report."""

    # constructor
    def __init__(self, parameters):
        # parameter validation using pydantic model
        if type(parameters) is MapathonRequestParams:
            self.params = parameters
        else:
            self.params = MapathonRequestParams(**parameters)

        self.database = Underpass(self.params)

    # Mapathon class instance method
    def get_summary(self):
        """Function to get summary of your mapathon event"""
        (
            osm_history_result,
            total_contributors,
        ) = self.database.get_mapathon_summary_result()
        mapped_features = [MappedFeature(**r) for r in osm_history_result]
        report = MapathonSummary(
            total_contributors=total_contributors[0].get("contributors_count", "None"),
            mapped_features=mapped_features,
        )
        return report

    def get_detailed_report(self):
        """Function to get detail report of your mapathon event. It includes individual user contribution"""
        (
            osm_history_result,
            total_contributors,
        ) = self.database.get_mapathon_detailed_result()
        mapped_features = [MappedFeatureWithUser(**r) for r in osm_history_result]
        contributors = [MapathonContributor(**r) for r in total_contributors]

        tm = TaskingManager(self.params)
        (
            tasks_mapped_results,
            tasks_validated_results,
        ) = tm.get_tasks_mapped_and_validated_per_user()
        (
            time_mapping_results,
            time_validating_results,
        ) = tm.get_time_spent_mapping_and_validating_per_user()
        (
            tasks_mapped_stats,
            tasks_validated_stats,
            time_mapping_stats,
            time_validating_stats,
        ) = ([], [], [], [])
        if len(tasks_mapped_results) > 0:
            for r in tasks_mapped_results:
                r[1] = r[1] if r[1] > 0 else 0
            tasks_mapped_stats = [MappedTaskStats(**r) for r in tasks_mapped_results]
        if len(tasks_validated_results) > 0:
            for r in tasks_validated_results:
                r[1] = r[1] if r[1] > 0 else 0
            tasks_validated_stats = [
                ValidatedTaskStats(**r) for r in tasks_validated_results
            ]
        if len(time_mapping_results) > 0:
            for t in time_mapping_results:
                t[1] = t[1].total_seconds() if t[1] else 0.0
            time_mapping_stats = [TimeSpentMapping(**r) for r in time_mapping_results]
        if len(time_validating_results) > 0:
            for t in time_validating_results:
                t[1] = t[1].total_seconds() if t[1] else 0.0
            time_validating_stats = [
                TimeSpentValidating(**r) for r in time_validating_results
            ]

        tm_stats = [
            TMUserStats(
                tasks_mapped=tasks_mapped_stats,
                tasks_validated=tasks_validated_stats,
                time_spent_mapping=time_mapping_stats,
                time_spent_validating=time_validating_stats,
            )
        ]

        report = MapathonDetail(
            contributors=contributors,
            mapped_features=mapped_features,
            tm_stats=tm_stats,
        )
        # print(Output(osm_history_query,self.con).to_list())
        return report


class Output:
    """Class to convert sql query result to specific output format. It uses Pandas Dataframe

    Parameters:
        supports : list, dict , json and sql query string along with connection

    Returns:
        json,csv,dict,list,dataframe
    """

    def __init__(self, result, connection=None):
        """Constructor"""
        if isinstance(result, (list, dict)):
            # print(type(result))
            try:
                self.dataframe = pandas.DataFrame(result)
            except Exception as err:
                raise err
        elif isinstance(result, str):
            check, r_json = check_for_json(result)
            if check is True:
                # print("i am json")
                try:
                    self.dataframe = pandas.json_normalize(r_json)
                except Exception as err:
                    raise err
            else:
                if connection is not None:
                    try:
                        self.dataframe = pandas.read_sql_query(result, connection)
                    except Exception as err:
                        raise err
                else:
                    raise ValueError("Connection is required for SQL Query")
        else:
            raise ValueError("Input type " + str(type(result)) + " is not supported")
        # print(self.dataframe)
        if self.dataframe.empty:
            return []

    def get_dataframe(self):
        """Functions    for getting the dataframe of the connection_params"""
        # print(self.dataframe)
        return self.dataframe

    def to_JSON(self):
        """Function to convert query result to JSON, Returns JSON"""
        # print(self.dataframe)
        js = self.dataframe.to_json(orient="records")
        return js

    def to_list(self):
        """Function to convert query result to list, Returns list"""

        result_list = self.dataframe.values.tolist()
        return result_list

    def to_dict(self):
        """Function to convert query result to dict, Returns dict"""
        dic = self.dataframe.to_dict(orient="records")
        return dic

    def to_CSV(self, output_file_path):
        """Function to return CSV data , takes output location string as input"""
        try:
            self.dataframe.to_csv(output_file_path, encoding="utf-8")
            return "CSV: Generated at : " + str(output_file_path)
        except Exception as err:
            raise err

    def to_GeoJSON(self, lat_column, lng_column):
        """to_Geojson converts pandas dataframe to geojson , Currently supports only Point Geometry and hence takes parameter of lat and lng ( You need to specify lat lng column )"""
        # print(self.dataframe)
        # columns used for constructing geojson object
        properties = self.dataframe.drop([lat_column, lng_column], axis=1).to_dict(
            "records"
        )

        features = self.dataframe.apply(
            lambda row: Feature(
                geometry=Point((float(row[lng_column]), float(row[lat_column]))),
                properties=properties[row.name],
            ),
            axis=1,
        ).tolist()

        # whole geojson object
        feature_collection = FeatureCollection(features=features)
        return feature_collection


class UserStats:
    def __init__(self):
        self.db = Database(get_db_connection_params("UNDERPASS"))
        self.con, self.cur = self.db.connect()

    def list_users(self, params):
        """returns a list of users in the database"""
        user_names_str = ",".join(["%s" for n in range(len(params.user_names))])

        query = sql.SQL(
            f"""SELECT distinct user_id, username AS user_name FROM changesets c
            INNER JOIN users u ON u.id = c.user_id
            WHERE c.created_at BETWEEN %s AND %s AND u.username IN ({user_names_str})
        """
        )

        items = (params.from_timestamp, params.to_timestamp, *params.user_names)

        list_users_query = self.cur.mogrify(query, items)

        result = self.db.executequery(list_users_query)

        users_list = [User(**r) for r in result]

        return users_list

    def get_statistics(self, params):
        """Returns statistics for the current user"""
        query = create_UserStats_get_statistics_query(params, self.con, self.cur)
        result = self.db.executequery(query)
        final_result = []
        for r in result:
            clean_result = dict_none_clean(dict(r))
            final_result.append(clean_result)
        summary = [UserStatistics(**r) for r in final_result]
        return summary

    def get_statistics_with_hashtags(self, params):
        """ "Returns user statistics for user with hashtags"""
        query = create_userstats_get_statistics_with_hashtags_query(
            params, self.con, self.cur
        )
        result = self.db.executequery(query)
        final_result = []
        for r in result:
            clean_result = dict_none_clean(dict(r))
            final_result.append(clean_result)
        summary = [UserStatistics(**r) for r in final_result]
        return summary


def dict_none_clean(to_clean):
    """Clean DictWriter"""
    result = {}
    for key, value in to_clean.items():
        if value is None:
            value = 0
        result[key] = value
    return result


class DataQualityHashtags:
    def __init__(self, params: DataQualityHashtagParams):
        self.db = Database(get_db_connection_params("UNDERPASS"))
        # self.db = Database(dict(config.items("UNDERPASS")))
        self.con, self.cur = self.db.connect()
        self.params = params

    @staticmethod
    def to_csv_stream(results):
        """Responsible for csv writing"""
        stream = StringIO()

        features = results.get("features")

        if len(features) == 0:
            return iter("")

        properties_keys = list(features[0].get("properties").keys())
        csv_keys = [*properties_keys, "latitude", "longitude"]

        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        for item in features:
            longitude, latitude = item.get("geometry").get("coordinates")
            row = {
                **item.get("properties"),
                "latitude": latitude,
                "longitude": longitude,
            }

            writer.writerow(row)

        return iter(stream.getvalue())

    @staticmethod
    def to_geojson(results):
        """Responseible for geojson writing"""
        features = []
        for row in results:
            geojson_feature = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row["lat"], row["lon"]]},
                "properties": {
                    "created_at": row["created_at"],
                    "changeset_id": row["changeset_id"],
                    "osm_id": row["osm_id"],
                    "issue_type": row["issues"].split(","),
                },
            }
            features.append(Feature(**geojson_feature))

        feature_collection = FeatureCollection(features=features)

        return feature_collection

    def get_report(self):
        """Function that returns data quality report"""
        query = generate_data_quality_hashtag_reports(self.cur, self.params)
        results = self.db.executequery(query)
        feature_collection = DataQualityHashtags.to_geojson(results)

        return feature_collection

    def get_report_summary(self):
        """Function that returns data quality report summary"""
        query = generate_data_quality_hashtag_reports_summary(self.cur, self.params)
        result = [dict(r) for r in self.db.executequery(query)]
        if result:
            df = pandas.DataFrame(result).set_index("value")
            stream = StringIO()
            df.to_csv(stream)
            return iter(stream.getvalue())
        return iter("")


class DataQuality:
    """Class for data quality report this is the class that self connects to database and provide you detail report about data quality inside specific tasking manager project

    Parameters:
           params and inputtype : Currently supports : TM for tasking manager id , username for OSM Username reports and hashtags for Osm hashtags
    Returns:
        [GeoJSON,CSV ]: [description]
    """

    def __init__(self, parameters, inputtype):
        self.db = Database(get_db_connection_params("UNDERPASS"))
        # self.db = Database(dict(config.items("UNDERPASS")))
        self.con, self.cur = self.db.connect()
        self.inputtype = inputtype
        # parameter validation using pydantic model
        if self.inputtype == "TM":
            if type(parameters) is DataQuality_TM_RequestParams:
                self.params = parameters
            else:
                self.params = DataQuality_TM_RequestParams(**parameters)
        elif self.inputtype == "username":
            if type(parameters) is DataQuality_username_RequestParams:
                self.params = parameters
            else:
                self.params = DataQuality_username_RequestParams(**parameters)
        else:
            raise ValueError("Input Type Must be in ['TM','username']")

    def get_report(self):
        """Functions that returns data_quality Report"""
        if self.inputtype == "TM":
            query = generate_data_quality_TM_query(self.params)
        elif self.inputtype == "username":
            query = generate_data_quality_username_query(self.params, self.cur)
        try:
            result = Output(query, self.con).to_GeoJSON("lat", "lng")
            return result
        except Exception as err:
            return err
        # print(result)

    def get_report_as_csv(self, filelocation):
        """Functions that returns data_quality Report as CSV Format , requires file path where csv is meant to be generated"""

        if self.inputtype == "TM":
            query = generate_data_quality_TM_query(self.params)
        elif self.inputtype == "username":
            query = generate_data_quality_username_query(self.params, self.cur)
        try:
            result = Output(query, self.con).to_CSV(filelocation)
            return result
        except Exception as err:
            return err


class Training:
    """[Class responsible for Training data API]"""

    def __init__(self):
        self.database = Underpass()

    def get_all_organisations(self):
        """[Generates result for all list of available organisations within the database.]

        Returns:
            [type]: [List of Training Organisations ( id, name )]
        """
        query_result = self.database.all_training_organisations()
        Training_organisations_list = [TrainingOrganisations(**r) for r in query_result]
        # print(Training_organisations_list)
        return Training_organisations_list

    def get_trainingslist(self, params: TrainingParams):
        """Returns  Training lists"""
        query_result = self.database.training_list(params)
        Trainings_list = [Trainings(**r) for r in query_result]
        # print(Trainings_list)
        return Trainings_list


class OrganizationHashtags:
    """[Class responsible for Organization Hashtag data API]"""

    def __init__(self, params: OrganizationHashtagParams):
        self.db = Database(get_db_connection_params("UNDERPASS"))
        self.con, self.cur = self.db.connect()
        self.params = params
        self.query = generate_organization_hashtag_reports(self.cur, self.params)

    def get_report(self):
        """Functions    that returns report of hashtags"""
        print(self.query)
        query_result = self.db.executequery(self.query)
        results = [OrganizationHashtag(**r) for r in query_result]
        return results

    def get_report_as_csv(self, filelocation):
        """Returns as csv report"""
        try:
            result = Output(self.query, self.con).to_CSV(filelocation)
            return result
        except Exception as err:
            return err


class Status:
    """Class to show how recent the data is from different data sources"""

    # constructor
    def __init__(self, parameters):
        # parameter validation using pydantic model
        if type(parameters) is DataRecencyParams:
            self.params = parameters
        else:
            self.params = DataRecencyParams(**parameters)

        self.database = Underpass(self.params)

    def get_osm_recency(self):
        """Returns OSM Recency"""
        # checks either that method is supported by the database supplied or not without making call to database class if yes will make a call else it will return None
        return (
            self.database.get_osm_last_updated()
            if getattr(self.database, "get_osm_last_updated", None)
            else None
        )

    def get_mapathon_statistics_recency(self):
        """Returns Mapathon recency"""
        return (
            self.database.get_mapathon_statistics_last_updated()
            if getattr(self.database, "get_mapathon_statistics_last_updated", None)
            else None
        )

    def get_user_statistics_recency(self):
        """Returns User stat recency"""
        return (
            self.database.get_user_statistics_last_updated()
            if getattr(self.database, "get_user_statistics_last_updated", None)
            else None
        )

    def get_user_data_quality_recency(self):
        """Returns Userdata quality recency"""
        return (
            self.database.get_user_data_quality_last_updated()
            if getattr(self.database, "get_user_data_quality_last_updated", None)
            else None
        )
