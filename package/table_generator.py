from typing import TypeVar

from peewee import *

TModel = TypeVar('TModel', bound=Model)

def generate_table(self: Database, model: TModel, class_name: str) -> None:
    type(class_name, (model,), {
        'Meta': type('Meta', (object,), {
            'database': self,
            'table_function': lambda c: c.__name__
        })
    }).create_table()

def attach_table_generator(db: Database) -> None:
    db.generate_table = lambda model, name: generate_table(db, model, name)
