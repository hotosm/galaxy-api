from pydantic import BaseModel
from typing import List


class User(BaseModel):
    user_id: int
    username: str = None
    gender: str = None
    osm_registration: str = None
    total_user_changesets: int
    added_highway: int
    modified_highway: int
    deleted_highway: int
    added_highway_km: float
    modified_highway_km: float
    deleted_highway_km: float

class UsersResult(BaseModel):
    users: List[User] = []