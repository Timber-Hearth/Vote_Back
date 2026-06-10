from pydantic import BaseModel


class VoteResponse(BaseModel):
    success: str
