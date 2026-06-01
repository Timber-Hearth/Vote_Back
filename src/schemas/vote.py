from typing import List

from pydantic import BaseModel, field_validator


class VoteRequest(BaseModel):
    option_ids: List[int]

    @field_validator("option_ids")
    @classmethod
    def ValidateOptionIds(cls, value: list[int]):
        if len(value) == 0:
            raise ValueError("at least one option required")

        if len(set(value)) != len(value):
            raise ValueError("duplicate option ids")

        return value