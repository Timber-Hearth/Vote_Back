from typing import List

from pydantic import BaseModel, field_validator

from src.schemas.responses.poll_group import Response_Option


class VoteRequest(BaseModel):
    vote_qr : str
    options: list[Response_Option]