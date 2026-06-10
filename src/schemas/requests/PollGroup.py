from datetime import datetime

from pydantic import BaseModel, field_validator

from src.schemas.requests import CreatePollRequest


# id | owner_id | is_public_result | is_closed | created_at | expire_at | delete_after_hours | title | description
class CreatePollGroupRequest(BaseModel):
    title: str
    owner_id: int
    description: str
    is_public_result: bool
    expire_at: datetime
    delete_after_hours: int
    polls: list[CreatePollRequest]

    @field_validator("delete_after_hours")
    @classmethod
    def ValidateDeleteAfterHours(cls, value:int) -> int:
        if value <= 0:
            raise ValueError("delete_after_hours must be greater than 0")
        return value

    @field_validator("polls")
    @classmethod
    def ValidatePolls(cls, value: list[CreatePollRequest]):
        if len(value) < 1:
            raise ValueError("polls must contain at least 1 poll")
        return value