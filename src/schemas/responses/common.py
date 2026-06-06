from pydantic import BaseModel


class RootResponse(BaseModel):
    Hello: str

