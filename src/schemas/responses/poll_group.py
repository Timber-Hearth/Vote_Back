from pydantic import BaseModel


class CreatePollDataResponse(BaseModel):
    title: str
    message: str
    tokens: str