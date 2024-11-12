import ast
from typing import List

from pydantic import BaseModel, Field, NonNegativeInt, field_validator, model_validator
from string_utils import is_full_string
from typing_extensions import Self

from reasoning_type import ReasoningType

class FramesBenchmarkRecord(BaseModel):
    id: NonNegativeInt = Field(alias='')
    prompt: str = Field(alias='Prompt')
    answer: str = Field(alias='Answer')
    wikipedia_links: List[str] = []
    reasoning_types: List[ReasoningType]
    wiki_links: List[str]

    @field_validator('wiki_links', mode='before')
    @classmethod
    def parse_wiki_links(cls, value) -> List[str]:
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value

    @field_validator('reasoning_types', mode='before')
    @classmethod
    def parse_reasoning_types(cls, value) -> List[ReasoningType]:
        if isinstance(value, str):
            return [ReasoningType(rt.strip()) for rt in value.split('|')]
        return value

    @model_validator(mode="before")
    def validate_model(self) -> Self:
        self['wikipedia_links'] = [s for s in [
            self['wikipedia_link_1'],
            self['wikipedia_link_2'],
            self['wikipedia_link_3'],
            self['wikipedia_link_4'],
            self['wikipedia_link_5'],
            self['wikipedia_link_6'],
            self['wikipedia_link_7'],
            self['wikipedia_link_8'],
            self['wikipedia_link_9'],
            self['wikipedia_link_10'],
            self['wikipedia_link_11+'],
        ] if is_full_string(s)]
        return self
