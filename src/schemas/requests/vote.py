from typing import List

from pydantic import BaseModel, field_validator


class VoteRequest(BaseModel):
    vote_data: dict[str, list[int]] # poll_id (qr아님, 그리고 투표 리스트)

