from anyio.abc import value
from numpy.lib.utils import source
from pytest import mark
from sqlalchemy import values

from package.change import *
from package.crud import *
from package.relation_kind import *

@mark.parametrize('entity_instance, relation, entity_to, entity_instance_to, expected', [
    (None, None, None, None, RelationKind.ENTITY),
    (None, None, None, 'Ij', RelationKind.ENTITY),
    (None, None, 'gh', None, RelationKind.ENTITY),
    (None, None, 'gh', 'Ij', RelationKind.ENTITY),
    (None, 'EF', None, None, RelationKind.ENTITY),
    (None, 'EF', None, 'Ij', RelationKind.ENTITY),
    (None, 'EF', 'gh', None, RelationKind.RELATION),
    (None, 'Ef', 'gh', 'Ij', RelationKind.RELATION),
    ('Cd', None, None, None, RelationKind.INSTANCE),
    ('Cd', None, None, 'Ij', RelationKind.INSTANCE),
    ('Cd', None, 'gh', None, RelationKind.INSTANCE),
    ('Cd', None, 'gh', 'Ij', RelationKind.INSTANCE),
    ('Cd', 'EF', None, None, RelationKind.INSTANCE),
    ('Cd', 'EF', None, 'Ij', RelationKind.INSTANCE),
    ('Cd', 'EF', 'gh', None, RelationKind.RELATION),
    ('Cd', 'Ef', 'gh', 'Ij', RelationKind.INSTANCE_RELATION),
])
def test_kind(
        entity_instance: str | None,
        relation: str | None,
        entity_to: str | None,
        entity_instance_to: str | None,
        expected: RelationKind
) -> None:
    assert expected == Change(
        crud=CRUD.READ,
        entity='ab',
        entity_instance=entity_instance,
        relation=relation,
        entity_to=entity_to,
        entity_instance_to=entity_instance_to
    ).kind()
