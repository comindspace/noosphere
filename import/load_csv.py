from csv import DictReader
from typing import TypeVar, Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def load_csv(path: str, record_type: Type[T], *args, **kwargs) -> list[T]:
    with open(path, "r", encoding="utf-8") as f:
        return [record_type.model_validate(row) for row in DictReader(f, *args, **kwargs)]
