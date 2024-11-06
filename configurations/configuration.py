import yaml
from inflection import *
from pydantic import BaseModel

from package.utilities import is_blank

class Configuration(BaseModel):
    @classmethod
    def grab(cls, configuration: dict, key: str | None = None):
        if key is None:
            return cls(**(configuration[underscore(cls.__name__.rstrip('Configuration'))]))
        else:
            if is_blank(key):
                return cls(**configuration)
            else:
                return cls(**configuration[key])

    @staticmethod
    def load(filepath: str) -> dict:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
