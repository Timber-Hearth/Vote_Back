from pydantic import BaseModel
from datetime import datetime


class Response_PollGroup_Token(BaseModel):
    title: str
    descrition: str
    qr_token: str
    is_public_result: bool
    is_closed: bool
    created_at: datetime
    expire_at: datetime
    delete_after_hours: int