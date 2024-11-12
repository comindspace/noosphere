from csv import DictReader
from typing import TypeVar, Type

T = TypeVar('T', bound='PydanticModel')

def load_csv(path: str, record_type: Type[T], *args, **kwargs) -> list[T]:
    with open(path) as f:
        return [record_type.model_validate(row) for row in DictReader(f, *args, **kwargs)]
