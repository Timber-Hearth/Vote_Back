from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthMessageResponse(BaseModel):
    message: str

