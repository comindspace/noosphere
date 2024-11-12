from dataclasses import dataclass

from string_utils import is_full_string

from package.crud import CRUD
from package.relation_kind import RelationKind

@dataclass
class Change:
    crud: CRUD
    entity: str
    entity_instance: str | None
    relation: str | None
    entity_to: str | None
    entity_instance_to: str | None

    def kind(self) -> RelationKind:
        if is_full_string(self.relation) and is_full_string(self.entity_to):
            if is_full_string(self.entity_instance) and is_full_string(self.entity_instance_to):
                return RelationKind.INSTANCE_RELATION
            else:
                return RelationKind.RELATION
        elif is_full_string(self.entity_instance):
            return RelationKind.INSTANCE
        else:
            return RelationKind.ENTITY
# 000 -> ENTITY
# 001 -> ENTITY
# 010 -> RELATION
# 011 -> RELATION
# 100 -> INSTANCE
# 101 -> INSTANCE
# 110 -> RELATION
# 111 -> INSTANCE_RELATION
# 
# *11*
#     1**1
#         INSTANCE_RELATION
#     else
#         RELATION
# 1***
#     INSTANCE
# else
#     ENTITY
# 
# 0000 -> ENTITY
# 0001 -> ENTITY
# 0010 -> ENTITY
# 0011 -> ENTITY
# 0100 -> ENTITY
# 0101 -> ENTITY
# 0110 -> RELATION
# 0111 -> RELATION
# 1000 -> INSTANCE
# 1001 -> INSTANCE
# 1010 -> INSTANCE
# 1011 -> INSTANCE
# 1100 -> INSTANCE
# 1101 -> INSTANCE
# 1110 -> RELATION
# 1111 -> INSTANCE_RELATION
