from pydantic import BaseModel
from typing import List

class User(BaseModel):
    user_id: int
    username: str = None
    # gender: str = None
    # osm_registration: str = None
    total_user_changesets: int = None
    filtered_osm_tag: str = 'highway'
    added: float
    modified: float
    deleted: float