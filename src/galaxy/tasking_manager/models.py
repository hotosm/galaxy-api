import psycopg2
import requests

from csv import DictWriter
from datetime import datetime
from enum import Enum
from io import StringIO
from ..validation.models import BaseModel

from pandas import DataFrame, pivot_table
from pydantic import validator

from typing import Optional, Any, List, cast, TypeVar, Generic, Type, Iterator, Dict
from typing_extensions import TypedDict, Protocol

from psycopg2.extras import DictCursor

from ..config import config

API_URL = "https://api.openstreetmap.org/api/0.6"

DBParams = TypedDict(
    "DBParams",
    {
        "host": str,
        "user": str,
        "password": str,
        "database": str,
        "port": int,
    },
)

T = TypeVar("T", bound="SupportCreate")


class SupportCreate(Protocol):
    @classmethod
    def create(cls: Type[T], items: Any) -> T:
        ...


class DbQuery(Generic[T]):
    def __init__(self, params: DBParams, model: Type[T]) -> None:
        self.conn = psycopg2.connect(**params)
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        self.model = model

    def execute_query(self, query: str) -> List[T]:
        self.cursor.execute(query)

        results = [self.model.create(items=r) for r in self.cursor.fetchall()]

        return results


class MappingLevel(Enum):
    """The mapping level the mapper has achieved"""

    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3


class ValidatorStats(BaseModel):
    project_id: int
    username: str
    user_id: int
    year: int
    validated_count: int
    countries: str
    mapping_level: int
    tasks_mapped: int
    tasks_validated: int

    @classmethod
    def create(cls: Type[T], items: Any) -> T:
        return cls(**items)

    @validator("mapping_level")
    def check_mapping_level(cls, value: int) -> str:
        return MappingLevel(value).name.lower()


def get_account_created(item: Dict[str, Any]) -> Dict[str, Any]:
    user_id = item["user_id"]
    resp = requests.get(f"{API_URL}/user/{user_id}.json")

    account_created = None

    if resp.status_code == 200:
        account_created = resp.json()["user"]["account_created"]

    new_item = {**item, "account_created": account_created}

    return new_item


def collect_account_created(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [get_account_created(i) for i in items]


class Team(BaseModel):
    id: int
    organisation_id: int
    organisation_name: str
    team_name: str
    managers: List[str]
    members_count: int

    @classmethod
    def create(cls: Type[T], items: Any) -> T:
        return cls(**items)

    def to_dict(self) -> Dict[str, Any]:
        item_dict = self.dict()
        item_dict = {**item_dict, "managers": ",".join(item_dict["managers"])}

        return item_dict


class ListTeamsRequest:
    @staticmethod
    def build_query() -> str:
        query = """with vt AS (SELECT distinct team_id as id from project_teams where role = 1 order by id),
            mu AS (SELECT tm.team_id, ARRAY_AGG(users.username) AS managers from team_members AS tm, vt, users WHERE users.id = tm.user_id AND tm.team_id = vt.id AND tm.function = 1 GROUP BY tm.team_id),
            uc AS (SELECT tm.team_id, count(tm.user_id) AS members_count from team_members AS tm, vt WHERE tm.team_id = vt.id GROUP BY tm.team_id)
            SELECT t.id, t.organisation_id, orgs.name AS organisation_name, t.name AS team_name, mu.managers, uc.members_count from teams AS t, mu, uc, organisations AS orgs where orgs.id = t.organisation_id AND t.id = mu.team_id AND t.id = uc.team_id"""

        return query

    @staticmethod
    def list_teams() -> Iterator[str]:
        tm_params = cast(DBParams, dict(config.items("TM")))
        db_conn = DbQuery(tm_params, Team)

        query = ListTeamsRequest.build_query()

        results = db_conn.execute_query(query)
        results_dicts = [r.to_dict() for r in results]

        stream = StringIO()

        csv_keys: List[str] = list(results_dicts[0].keys())
        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        [writer.writerow(row) for row in results_dicts]

        return iter(stream.getvalue())


class ValidatorStatsRequest(BaseModel):
    year: int = 2012
    country: Optional[str] = None
    organisation: Optional[str] = None

    def build_query(self, cur: DictCursor) -> str:
        project_ids_filters = [f"date_part('year', created) > {self.year}"]

        if self.organisation is not None:
            stmt = psycopg2.sql.SQL(
                "organisation_id in (SELECT id from organisations where name = %s)"
            )
            org_query = cur.mogrify(stmt, (self.organisation,)).decode()
            project_ids_filters.append(org_query)

        if self.country is not None:
            stmt = psycopg2.sql.SQL("%s = ANY(country)")
            country_query = cur.mogrify(stmt, (self.country,)).decode()
            project_ids_filters.append(country_query)

        filters_str = " AND ".join(project_ids_filters)
        ids_subquery = f"""WITH projects AS (select id,
                country,
                tasks_mapped,
                tasks_validated,
                created from projects WHERE {filters_str})"""

        query = f"""{ids_subquery}
            SELECT th.project_id,
                th.user_id,
                users.username,
                users.mapping_level,
                date_part('year', th.action_date) AS year,
                array_to_string(projects.country, ',') AS countries,
                projects.tasks_mapped,
                projects.tasks_validated,
                count(th.action_text) AS validated_count
            FROM projects, task_history AS th, users
            WHERE th.project_id = projects.id AND
                th.action_text = 'VALIDATED' AND
                users.id = th.user_id
            GROUP BY th.project_id,
                th.user_id,
                users.username,
                users.mapping_level,
                year,
                projects.country,
                projects.tasks_mapped,
                projects.tasks_validated
            ORDER BY year ASC, th.project_id;"""

        return query

    def run(self) -> Iterator[str]:
        tm_params = cast(DBParams, dict(config.items("TM")))
        db_conn = DbQuery(tm_params, ValidatorStats)

        query = self.build_query(db_conn.cursor)

        results = db_conn.execute_query(query)

        items = [r.dict() for r in results]

        items_with_registered = collect_account_created(items)

        df = DataFrame(items_with_registered)

        grouped_items = [
            "project_id",
            "user_id",
            "username",
            "countries",
            "mapping_level",
            "tasks_mapped",
            "tasks_validated",
            "account_created",
        ]

        out = (
            pivot_table(
                df,
                values="validated_count",
                index=grouped_items,
                columns="year",
                fill_value=0,
            )
            .swaplevel(0, 1)
            .reset_index()
        )

        rows_list = out.to_dict("records")

        stream = StringIO()

        csv_keys: List[str] = list(rows_list[0].keys())
        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        [writer.writerow(row) for row in rows_list]

        return iter(stream.getvalue())


class TeamMemberFunctions(Enum):
    """Describes the function a member can hold within a team"""

    MANAGER = 1
    MEMBER = 2


class TeamMetadata(BaseModel):
    team_id: int
    team_name: str
    organisation_id: int
    organisation_name: str
    user_id: int
    username: str
    function: int

    @classmethod
    def create(cls: Type[T], items: Any) -> T:
        return cls(**items)

    @validator("function")
    def check_function(cls, value: int) -> str:
        return TeamMemberFunctions(value).name.lower()

    def to_dict(self) -> Dict[str, Any]:
        item_dict = self.dict()
        return item_dict


class ListTeamsMetadataRequest:
    @staticmethod
    def build_query() -> str:
        query = """
            with vt AS (SELECT distinct team_id as id from project_teams where role = 1 order by id),
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

    @staticmethod
    def list() -> Iterator[str]:
        tm_params = cast(DBParams, dict(config.items("TM")))
        db_conn = DbQuery(tm_params, TeamMetadata)

        query = ListTeamsMetadataRequest.build_query()

        results = db_conn.execute_query(query)
        results_dicts = [r.to_dict() for r in results]

        stream = StringIO()

        csv_keys: List[str] = list(results_dicts[0].keys())
        writer = DictWriter(stream, fieldnames=csv_keys)
        writer.writeheader()

        [writer.writerow(row) for row in results_dicts]

        return iter(stream.getvalue())
