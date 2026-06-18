from pydantic import BaseModel
from datetime import datetime


class Response_Option(BaseModel):
    option_text: str
    display_order: int


class Response_Poll(BaseModel):
    title: str
    description: str
    allow_multiple_choice: bool
    options: list[Response_Option]


class Response_PollGroup_Token(BaseModel):
    message: str
    data: list[Response_Poll]
