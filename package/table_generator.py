from typing import TypeVar

from peewee import *

TModel = TypeVar('TModel', bound=Model)

def generate_table(self: Database, model: TModel, class_name: str, dictionary: dict[str, Field] | None = None) -> None:
    type(class_name, (model,), {
        'Meta': type('Meta', (object,), {
            'database': self,
            'table_function': lambda c: c.__name__,
        }),
        **({} if dictionary is None else dictionary),
    }).create_table()

def attach_table_generator(database: Database) -> None:
    database.generate_table = lambda model, name, dictionary=None: generate_table(database, model, name, dictionary)
