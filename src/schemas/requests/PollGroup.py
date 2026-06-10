from datetime import datetime

from pydantic import BaseModel, field_validator

from src.schemas.requests import CreatePollRequest


class Get_PollGroupRequest(BaseModel):
    token: str