import yaml
from inflection import *
from pydantic import BaseModel
from string_utils import is_full_string

class Configuration(BaseModel):
    @classmethod
    def grab(cls, configuration: dict, key: str | None = None):
        if key is None:
            return cls(**(configuration[underscore(cls.__name__.rstrip('Configuration'))]))
        else:
            if is_full_string(key):
                return cls(**configuration[key])
            else:
                return cls(**configuration)

    @staticmethod
    def load(filepath: str) -> dict:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
