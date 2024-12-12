import ast
from typing import List

from pydantic import BaseModel, Field, NonNegativeInt, field_validator

from reasoning_type import ReasoningType

class FramesBenchmarkRecord(BaseModel):
    id: NonNegativeInt = Field(alias="")
    prompt: str = Field(alias="Prompt")
    answer: str = Field(alias="Answer")
    reasoning_types: List[ReasoningType]
    wiki_links: List[str]

    @field_validator("wiki_links", mode="before")
    @classmethod
    def parse_wiki_links(cls, value) -> List[str]:
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value

    @field_validator("reasoning_types", mode="before")
    @classmethod
    def parse_reasoning_types(cls, value) -> List[ReasoningType]:
        if isinstance(value, str):
            return [ReasoningType(rt.strip()) for rt in value.split("|")]
        return value
