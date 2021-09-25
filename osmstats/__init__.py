from configparser import ConfigParser
from pydantic import BaseModel as PydanticModel

config = ConfigParser()
config.read("config.txt")


def to_camel(string: str) -> str:
    split_string = string.split("_")

    return "".join(
        [split_string[0], *[w.capitalize() for w in split_string[1:]]]
    )


class BaseModel(PydanticModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
