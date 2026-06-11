from datetime import datetime

from pydantic import BaseModel, field_validator

from src.schemas.requests import CreatePollRequest


class Get_PollGroupRequest(BaseModel):
    token: str

class Request_Create_PollGroup(BaseModel):
    title : str
    description : str
    created_at : str
    delete_after_hours : str
    is_public_result : str
    expire_at : str
    poll_data_list : list[SinglePollData]
    options : list[OptionData]

    @field_validator("polls")
    def validate_polls(cls, value):
        if not value:
            raise ValueError("투표는 최소 하나 이상이어야 합니다.")
        return value

class SinglePollData(BaseModel):
    title : str
    description : str
    allow_multiple_choice : bool
    options : list[OptionData]

class OptionData(BaseModel):
    option_text : str
    display_order : int